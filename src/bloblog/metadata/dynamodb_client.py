"""
DynamoDB implementation of the MetadataClient interface.
"""

import boto3
from typing import List, Optional
import botocore.exceptions
from .metadata_client import MetadataClient
from .file_metadata import FileMetadata

class DynamoDBClient(MetadataClient):
    """
    Handles metadata operations using a DynamoDB table.
    """
    def __init__(self, table_name: str):
        """
        :param table_name: Name of the DynamoDB table.
        """
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def add(self, item: FileMetadata) -> None:
        """See base class docstring."""
        try:
            self.table.put_item(Item=item.__dict__)
        except botocore.exceptions.ClientError as e:
            # Handle the error appropriately
            raise e

    def update(self, item: FileMetadata) -> None:
        """See base class docstring."""
        try:
            self.table.update_item(
                Key={'uuid': item.uuid},
                UpdateExpression="set relative_path=:rp, last_modified=:lm, upload_status=:us, sha256=:sh, cache_control=:cc, content_type=:ct",
                ExpressionAttributeValues={
                    ':rp': item.relative_path,
                    ':lm': item.last_modified,
                    ':us': item.upload_status,
                    ':sh': item.sha256,
                    ':cc': item.cache_control,
                    ':ct': item.content_type
                }
            )
        except botocore.exceptions.ClientError as e:
            # Handle the error appropriately
            raise e
    
    def get_file_metadata(self, relative_path: str) -> Optional[FileMetadata]:
        """See base class docstring."""
        try:
            response = self.table.query(
                IndexName='RelativePathIndex',
                KeyConditionExpression='relative_path = :rp',
                ExpressionAttributeValues={':rp': relative_path}
            )
            items = response.get('Items', [])
            if not items:
                return None
            return FileMetadata(**items[0])
        except botocore.exceptions.ClientError as e:
            # Handle the error appropriately
            raise e

    def fetch_all_records(self) -> List[FileMetadata]:
        """See base class docstring."""
        items = []
        try:
            paginator = self.dynamodb.meta.client.get_paginator('scan')
            for page in paginator.paginate(TableName=self.table_name):
                items.extend(page.get('Items', []))
            return [FileMetadata(**item) for item in items]
        except botocore.exceptions.ClientError as e:
            # Handle the error appropriately
            raise e

    def delete(self, item: FileMetadata) -> None:
        """See base class docstring."""
        try:
            self.table.delete_item(Key={'uuid': item.uuid})
        except botocore.exceptions.ClientError as e:
            raise e
