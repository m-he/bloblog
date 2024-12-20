"""
S3 client for handling file operations on AWS S3.
"""

import boto3
from botocore.exceptions import ClientError
from bloblog.metadata.file_metadata import FileMetadata
import os

class S3Client:
    """
    Interacts with AWS S3 to upload, delete, and update file metadata.
    """
    def __init__(self, bucket_name: str):
        """
        :param bucket_name: S3 bucket name.
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')

    def upload_file(self, metadata: FileMetadata, sync_root: str) -> None:
        """
        Upload a file to S3.

        :param metadata: FileMetadata describing the file.
        """
        try:
            self.s3_client.upload_file(
                os.path.join(sync_root, metadata.relative_path),
                self.bucket_name,
                metadata.relative_path,
                ExtraArgs={
                    'CacheControl': metadata.cache_control,
                    'ContentType': metadata.content_type,
                    'Metadata': {'uuid': metadata.uuid}
                }
            )
        except ClientError as e:
            print(f"Failed to upload {metadata.relative_path} to S3: {e}")

    def delete_file(self, metadata: FileMetadata) -> None:
        """
        Delete a file from S3 by key.

        :param s3_key: The S3 key of the file.
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=metadata.relative_path)
        except ClientError as e:
            print(f"Failed to delete {metadata.relative_path} from S3: {e}")

    def update_file_metadata(self, metadata: FileMetadata) -> None:
        """
        Update a file's metadata in S3.

        :param metadata: FileMetadata with updated info.
        """
        try:
            self.s3_client.copy_object(
                Bucket=self.bucket_name,
                CopySource={'Bucket': self.bucket_name, 'Key': metadata.relative_path},
                Key=metadata.relative_path,
                MetadataDirective='REPLACE',
                Metadata={'uuid': metadata.uuid, 'cache-control': metadata.cache_control, "ContentType": metadata.content_type}
            )
        except ClientError as e:
            print(f"Failed to update metadata for {metadata.relative_path} in S3: {e}")
