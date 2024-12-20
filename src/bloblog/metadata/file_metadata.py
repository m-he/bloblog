from dataclasses import dataclass

"""
Data container for file metadata involved in synchronization.
"""

@dataclass
class FileMetadata:
    """
    Represents metadata of a file being tracked.

    :param uuid: Unique identifier for the file.
    :param relative_path: Relative path of the file from the sync root.
    :param last_modified: Timestamp of the file's last modification.
    :param upload_status: upload_pending, delete_pending, update_pending or uploaded
    :param sha256: SHA-256 hash of the file content.
    :param cache_control: Cache-Control header for the file.
    """
    uuid: str
    relative_path: str
    last_modified: str
    upload_status: str
    sha256: str
    cache_control: str
    content_type: str
