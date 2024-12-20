from bloblog.config.config_manager import ConfigManager
from pytest import fixture

@fixture
def config():
    return ConfigManager('/workspaces/bloblog/tests/data/test-config.yaml')

def test_deployment_storage(config):
    deployment = config.config['deployment'][0]['storage']
    assert deployment['type'] == 's3'
    assert deployment['name'] == 'my-sync-bucket'

def test_deployment_metadb(config):
    metadb = config.config['deployment'][0]['metadb']
    assert metadb['type'] == 'dyanmodb'
    assert metadb['dbname'] == 'dyanmodb'
    assert metadb['name'] == 'my-sync-table'

def test_logging_config(config):
    logging = config.config['logging']
    assert logging['level'] == 'INFO'
    assert logging['format'] == 'json'
    assert logging['output'] == 'stdout'

def test_cache_control_default(config):
    default = config.config['cache_control']['default']
    assert default['max-age'] == 3600
    assert default['settings'] == 'public,must-revalidate'

def test_cache_control_rules(config):
    rules = config.config['cache_control']['rules']
    assert len(rules) == 2
    assert 'mimetype' in rules[0]
    assert 'settings' in rules[0]
    assert 'age' in rules[0]

def test_sync_settings(config):
    sync = config.config['sync']
    assert sync['root_path'] == '/path/to/local/directory'
    assert '*.tmp' in sync['exclude_patterns']

def test_workers(config):
    assert config.get_workers() == 5
