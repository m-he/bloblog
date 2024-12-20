"""
Manages application configuration including cache control logic.
"""

import yaml
from typing import List
from datetime import datetime, timedelta
from bloblog.metadata.file_metadata import FileMetadata
import mimetypes


class ConfigManager:
    """
    Manages application configuration from a YAML file and provides related logic 
    such as determining cache control headers.
    """
    def __init__(self, config_file: str):
        """
        Initialize the ConfigManager with a given configuration file.

        :param config_file: Path to the configuration YAML file.
        """
        with open(config_file, 'r') as file:
            self.config = yaml.safe_load(file)

    def get_sync_root_path(self) -> str:
        """
        Retrieve the local directory path that should be synchronized.

        :return: The directory path as a string.
        """
        return self.config['sync']['root_path']

    def get_exclude_patterns(self) -> List[str]:
        """
        Retrieve a list of file patterns to exclude from synchronization.

        :return: List of glob patterns.
        """
        return self.config['sync']['exclude_patterns']

    def get_workers(self) -> int:
        """
        Retrieve the number of workers for parallel processing.

        :return: The number of workers as an integer.
        """
        return self.config.get('workers', 1)

    def cache_control(self, file_metadata: FileMetadata) -> FileMetadata:
        """
        Determine the appropriate Cache-Control header for a given file.

        :param file_metadata: A FileMetadata instance.
        :return: the updated FileMetadata instance.
        """
        default_cache_control = self.config['cache_control']['default']
        rules = self.config['cache_control']['rules']
        last_modified = datetime.strptime(file_metadata.last_modified, "%Y-%m-%dT%H:%M:%S")
        file_metadata.cache_control = f"max-age={default_cache_control['max-age']},{default_cache_control['settings']}"

        for rule in rules:
            if file_metadata.content_type in rule['mimetype']:
                for age_rule in rule['age']:
                    item_time = self._parse_age(age_rule['item'])
                    max_time = self._parse_age(age_rule['max'])
                    if datetime.now() - last_modified > item_time:
                        file_metadata.cache_control = f"max-age={int(max_time.total_seconds())},{rule['settings']}"
                    else:
                        break
                else:
                    continue
                break
        return file_metadata

    def _parse_age(self, age_str: str) -> timedelta:
        """
        Parse an age string into a timedelta object.

        :param age_str: Age string (e.g., "1w", "1m").
        :return: A timedelta object.
        """
        unit = age_str[-1]
        value = int(age_str[:-1])
        if unit == 'd':
            return timedelta(days=value)
        elif unit == 'w':
            return timedelta(weeks=value)
        elif unit == 'm':
            return timedelta(days=value * 30)
        elif unit == 'y':
            return timedelta(days=value * 365)
        else:
            raise ValueError(f"Unknown age unit: {unit}")
