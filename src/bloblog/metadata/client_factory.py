"""
Factory for creating MetadataClient instances based on db type.
"""

from .metadata_client import MetadataClient
from .dynamodb_client import DynamoDBClient

class MetadataClientFactory:
    """
    Factory to create MetadataClient instances for different database types 
    (e.g., DynamoDB, Elasticsearch, SimpleDB).
    """
    def get_client(self, db_config: dict) -> MetadataClient:
        """
        Return a MetadataClient instance for the given db_type.

        :param db_type: 'dynamodb', 'elasticsearch', 'simpledb', etc.
        :return: A MetadataClient instance.
        """
        if db_config['type'] == 'dynamodb':
            return DynamoDBClient(db_config['name'])
        else:
            raise ValueError(f"Unsupported db_type: {db_config['type']}")
