"""
Manages the synchronization process between local files and S3.
"""

from typing import NoReturn
from bloblog.metadata.metadata_client import MetadataClient
from bloblog.storage.s3_client import S3Client
from bloblog.config.config_manager import ConfigManager
from .task_queue import TaskQueue
from bloblog.metadata.file_metadata import FileMetadata
import os
import hashlib
import re
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import mimetypes
import threading

class FileSynchronizer:
    """
    Orchestrates the full synchronization workflow.
    """
    def __init__(
        self,
        metadata_client: MetadataClient,
        s3_client: S3Client,
        config_manager: ConfigManager,
        task_queue: TaskQueue
    ):
        """
        :param metadata_client: For DB operations on metadata.
        :param s3_client: For S3 operations.
        :param config_manager: For configuration & cache control logic.
        :param task_queue: For managing upload/delete/update tasks.
        """
        self.metadata_client = metadata_client
        self.s3_client = s3_client
        self.config_manager = config_manager
        self.task_queue = task_queue

    def start_synchronization(self) -> NoReturn:
        """
        Begin the synchronization process:
        - Update metadata statuses
        - Walk local files
        - Compare with DB metadata
        - Enqueue tasks
        - Process tasks concurrently
        """
        self._update_metadata_statuses()

        # Event to signal when walk_files is done
        self.walk_files_done = threading.Event()

        # Start walk_files and process_queues in separate threads
        walk_thread = threading.Thread(target=self.walk_files)
        process_thread = threading.Thread(target=self.process_queues)

        walk_thread.start()
        process_thread.start()

        walk_thread.join()
        self.walk_files_done.set()
        process_thread.join()

    def _update_metadata_statuses(self) -> None:
        """
        Update all upload_status to delete_pending.
        """
        records = self.metadata_client.fetch_all_records()
        for record in records:
            record.upload_status = 'delete_pending'
            self.metadata_client.update(record)

    def _delete_pending_files(self) -> None:
        """
        Delete all files with upload_status 'delete_pending'.
        """
        records = self.metadata_client.fetch_all_records()
        for record in records:
            if record.upload_status == 'delete_pending':
                self.s3_client.delete_file(record)
                self.metadata_client.delete(record)

    def walk_files(self) -> None:
        """
        Enumerate local files in the sync root and identify which need actions.
        """
        files_to_process = []
        for root, _, files in os.walk(self.config_manager.get_sync_root_path()):
            for file in files:
                file_path = os.path.join(root, file)
                files_to_process.append(file_path)
        
        with ThreadPoolExecutor(max_workers=self.config_manager.get_workers()) as executor:
            futures = [executor.submit(self._process_file, file_path) for file_path in files_to_process]
            for future in as_completed(futures):
                future.result()

    def _process_file(self, file_path: str) -> None:
        """
        Process a single file to determine if it should be excluded or enqueued for a task.
        """
        if self._should_exclude(file_path):
            return

        relative_path = os.path.relpath(file_path, self.config_manager.get_sync_root_path())
        file_metadata = self.metadata_client.get_file_metadata(relative_path)
        if file_metadata:
            self._compare_and_enqueue(file_path, file_metadata)
        else:
            file_metadata = FileMetadata(
                uuid=str(uuid.uuid4()),
                relative_path=relative_path,
                last_modified=datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%dT%H:%M:%S"),
                upload_status='upload_pending',
                sha256=self._calculate_sha256(file_path),
                cache_control='',
                content_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            )
            file_metadata = self.config_manager.cache_control(file_metadata)
            self.task_queue.enqueue(file_metadata)

    def _should_exclude(self, file_path: str) -> bool:
        """
        Check if the file should be excluded based on the exclude patterns.
        """
        for pattern in self.config_manager.get_exclude_patterns():
            try:
                if isinstance(pattern, str):
                    # Treat pattern as literal string if it's not a valid regex
                    escaped_pattern = re.escape(pattern)
                    if re.search(escaped_pattern, file_path):
                        return True
            except re.error:
                continue
        return False

    def _compare_and_enqueue(self, file_path: str, file_metadata: FileMetadata) -> None:
        """
        Compare the local file with its metadata and enqueue tasks based on the comparison.
        """
        local_sha256 = self._calculate_sha256(file_path)
        if local_sha256 != file_metadata.sha256:
            file_metadata.upload_status = 'upload_pending'
            file_metadata.last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%dT%H:%M:%S")
            file_metadata = self.config_manager.cache_control(file_metadata)
            self.task_queue.enqueue(file_metadata)
        else:
            checked_file = self.config_manager.cache_control(file_metadata)
            if checked_file.cache_control != file_metadata.cache_control:
                checked_file.upload_status = 'update_pending'
                self.task_queue.enqueue(checked_file)
            else:
                file_metadata.upload_status = 'uploaded'
                self.task_queue.enqueue(file_metadata)
    
    def _calculate_sha256(self, file_path: str) -> str:
        """
        Calculate the SHA-256 hash of the file.
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def process_queues(self) -> None:
        """
        Process all pending tasks (upload, delete, update) until all tasks are done.
        """
        with ThreadPoolExecutor(max_workers=self.config_manager.get_workers()) as executor:
            futures = []
            while not (self.task_queue.is_empty() and self.walk_files_done.is_set()):
                if not self.task_queue.is_empty():
                    file_metadata = self.task_queue.dequeue()
                    if file_metadata:
                        futures.append(executor.submit(self._process_task, file_metadata))
            for future in as_completed(futures):
                future.result()

    def _process_task(self, file_metadata: FileMetadata) -> None:
        """
        Process a single task based on its operation type.
        """
        action_map = {
            'upload_pending': self._handle_upload,
            'delete_pending': self._handle_delete,
            'update_pending': self._handle_update,
            'uploaded': self._handle_uploaded
        }

        handler = action_map.get(file_metadata.upload_status)
        if handler:
            handler(file_metadata)

    def _handle_upload(self, file_metadata: FileMetadata) -> None:
        self.s3_client.upload_file(file_metadata, self.config_manager.get_sync_root_path())
        file_metadata.upload_status = 'uploaded'
        self.metadata_client.update(file_metadata)

    def _handle_delete(self, file_metadata: FileMetadata) -> None:
        self.s3_client.delete_file(file_metadata)
        self.metadata_client.delete(file_metadata)

    def _handle_update(self, file_metadata: FileMetadata) -> None:
        self.s3_client.update_file_metadata(file_metadata)
        file_metadata.upload_status = 'uploaded'
        self.metadata_client.update(file_metadata)

    def _handle_uploaded(self, file_metadata: FileMetadata) -> None:
        self.metadata_client.update(file_metadata)
