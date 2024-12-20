"""
Entry point for the bloblog synchronization tool. 
Uses argparse to accept a --config argument that points to a config.yaml file.
"""

import argparse
from bloblog.config.config_manager import ConfigManager
from bloblog.metadata.client_factory import MetadataClientFactory
from bloblog.storage.s3_client import S3Client
from bloblog.sync.task_queue import TaskQueue
from bloblog.sync.file_synchronizer import FileSynchronizer

def main():
    """
    Main entry point for the application.
    Parses command-line arguments to obtain the config file path and then 
    initiates the synchronization process using FileSynchronizer.
    """
    parser = argparse.ArgumentParser(description="Run the bloblog file synchronization.")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the YAML configuration file."
    )
    args = parser.parse_args()

    # Instantiate ConfigManager
    config_manager = ConfigManager(args.config)
    config = config_manager.config

    # Initialize MetadataClient using MetadataClientFactory
    metadata_client_factory = MetadataClientFactory()
    metadata_client = metadata_client_factory.get_client(config['deployment']['metadb'])

    # Initialize S3Client
    s3_client = S3Client(
        bucket_name=config['deployment']['storage']['name']
    )

    # Initialize TaskQueue without workers parameter
    task_queue = TaskQueue()

    # Create FileSynchronizer with config_manager
    file_synchronizer = FileSynchronizer(
        metadata_client=metadata_client,
        s3_client=s3_client,
        config_manager=config_manager,
        task_queue=task_queue
    )

    # Start synchronization
    file_synchronizer.start_synchronization()

if __name__ == "__main__":
    main()
