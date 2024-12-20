"""
Interface for metadata database operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .file_metadata import FileMetadata

class MetadataClient(ABC):
    """
    Abstract interface for metadata database operations.
    """
    @abstractmethod
    def add(self, item: FileMetadata) -> None:
        """
        Add a new file metadata record.

        :param item: The FileMetadata object.
        """
        pass

    @abstractmethod
    def update(self, item: FileMetadata) -> None:
        """
        Update an existing file metadata record.

        :param item: The updated FileMetadata object.
        """
        pass

    @abstractmethod
    def get_file_metadata(self, relative_path: str) -> Optional[FileMetadata]:
        """
        Get file metadata by its relative path.

        :param relative_path: The relative path of the file.
        :return: FileMetadata or None if not found.
        """
        pass

    @abstractmethod
    def fetch_all_records(self) -> List[FileMetadata]:
        """
        Fetch all file metadata records.

        :return: A list of FileMetadata objects.
        """
        pass
