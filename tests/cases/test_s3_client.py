from unittest.mock import patch, MagicMock
from bloblog.storage.s3_client import S3Client
from bloblog.metadata.file_metadata import FileMetadata

class TestS3Client:  # Removed unittest.TestCase
    @patch('bloblog.storage.s3_client.boto3.client')
    def test_upload_file_success(self, mock_boto3_client):
        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3
        client = S3Client(bucket_name='test-bucket')
        metadata = FileMetadata(
            relative_path='path/to/file.txt',
            uuid='123',
            cache_control='no-cache',
            last_modified='2023-10-10T10:00:00Z',
            upload_status='success',
            sha256='abcdef1234567890'
        )

        client.upload_file(metadata, '/sync')

        mock_s3.upload_file.assert_called_once_with(
            '/sync/path/to/file.txt',
            'test-bucket',
            'path/to/file.txt',
            ExtraArgs={'Metadata': {'uuid': '123', 'cache-control': 'no-cache'}}
        )

    @patch('bloblog.storage.s3_client.boto3.client')
    def test_delete_file_success(self, mock_boto3_client):
        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3
        client = S3Client(bucket_name='test-bucket')
        metadata = FileMetadata(
            relative_path='path/to/file.txt',
            uuid='123',
            cache_control='no-cache',
            last_modified='2023-10-10T10:00:00Z',
            upload_status='success',
            sha256='abcdef1234567890'
        )

        client.delete_file(metadata)

        mock_s3.delete_object.assert_called_once_with(
            Bucket='test-bucket',
            Key='path/to/file.txt'
        )

    @patch('bloblog.storage.s3_client.boto3.client')
    def test_update_file_metadata_success(self, mock_boto3_client):
        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3
        client = S3Client(bucket_name='test-bucket')
        metadata = FileMetadata(
            relative_path='path/to/file.txt',
            uuid='123',
            cache_control='no-cache',
            last_modified='2023-10-10T10:00:00Z',
            upload_status='success',
            sha256='abcdef1234567890'
        )

        client.update_file_metadata(metadata)

        mock_s3.copy_object.assert_called_once_with(
            Bucket='test-bucket',
            CopySource={'Bucket': 'test-bucket', 'Key': 'path/to/file.txt'},
            Key='path/to/file.txt',
            MetadataDirective='REPLACE',
            Metadata={'uuid': '123', 'cache-control': 'no-cache'}
        )

    def test_e2e_upload_file(self):
        client = S3Client(bucket_name='test-freevolution.me')
        metadata = FileMetadata(
            relative_path='posts/index.html',
            uuid='123',
            cache_control='no-cache',
            last_modified='2023-10-10T10:00:00Z',
            upload_status='success',
            sha256='abcdef1234567890'
        )

        client.upload_file(metadata, '/workspaces/bloblog/tests/data')
    
    def test_e2e_update_file(self):
        client = S3Client(bucket_name='test-freevolution.me')
        metadata = FileMetadata(
            relative_path='posts/index.html',
            uuid='123',
            cache_control='max-age=3600, public',
            last_modified='2023-10-10T10:00:00Z',
            upload_status='success',
            sha256='abcdef1234567890'
        )

        client.update_file_metadata(metadata)
    
    def test_e2e_delete_file(self):
        client = S3Client(bucket_name='test-freevolution.me')
        metadata = FileMetadata(
            relative_path='posts/index.html',
            uuid='123',
            cache_control='max-age=3600, public',
            last_modified='2023-10-10T10:00:00Z',
            upload_status='success',
            sha256='abcdef1234567890'
        )

        client.delete_file(metadata)