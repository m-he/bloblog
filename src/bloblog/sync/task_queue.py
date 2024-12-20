"""
Implements tasks and task queues for the synchronization process.
"""

from typing import Optional
from collections import deque
from bloblog.metadata.file_metadata import FileMetadata

class TaskQueue:
    """
    In-memory queue for managing a collection of tasks.
    """
    def __init__(self):
        """
        Initialize an empty task queue.
        """
        self._queue = deque()

    def enqueue(self, file_metadata: FileMetadata) -> None:
        """
        Add a file metadata to the queue.

        :param file_metadata: FileMetadata instance to add.
        """
        self._queue.append(file_metadata)

    def dequeue(self) -> Optional[FileMetadata]:
        """
        Remove and return the next file metadata in the queue, if any.

        :return: A FileMetadata or None if empty.
        """
        if self._queue:
            return self._queue.popleft()
        return None

    def is_empty(self) -> bool:
        """
        Check whether the queue is empty.

        :return: True if empty, False otherwise.
        """
        return not self._queue
