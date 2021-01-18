import pytest

import os

import json

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize('name', [
  ('influxdb2'),
])
def test_packages_are_installed(host, name):
    package = host.package(name)
    assert package.is_installed


@pytest.mark.parametrize('username,groupname,path', [
  ('influxdb', 'influxdb', '/etc/influxdb/config.yml'),
  ('root', 'root', '/etc/default/influxdb2'),
])
def test_logstash_config_file(host, username, groupname, path):
    config = host.file(path)
    assert config.exists
    assert config.is_file
    assert config.user == username
    assert config.group == groupname


def test_influxdb_replies_to_ping(host):
    command = 'influx ping'
    ping = host.check_output(command)
    assert ping == 'OK'


@pytest.mark.parametrize('name,description', [
  ('example-org', ''),
  ('main-org', 'Main organization'),
  ('guest-org', ''),
])
def test_influxdb_organizations_exist(host, name, description):
    command = 'influx org ls --json'
    json_data = host.check_output(command)
    items_list = json.loads(json_data)
    for item in items_list:
        if item['name'] == name and item['description'] == description:
            assert True
            break
    else:
        assert False


@pytest.mark.parametrize('name', [
  ('example-user'),
  ('admin01'),
  ('guest01'),
])
def test_influxdb_users_exist(host, name):
    command = 'influx user ls --json'
    json_data = host.check_output(command)
    items_list = json.loads(json_data)
    for item in items_list:
        if item['name'] == name:
            assert True
            break
    else:
        assert False


@pytest.mark.parametrize('name,description,org', [
  ('example-bucket', '', 'example-org'),
  ('bucket01', 'First bucket', 'main-org'),
  ('bucket02', '', 'main-org'),
])
def test_influxdb_buckets_exist(host, name, description, org):
    command = f'influx bucket ls --json --org {org}'
    json_data = host.check_output(command)
    items_list = json.loads(json_data)
    for item in items_list:
        if item['name'] == name and item['description'] == description:
            assert True
            break
    else:
        assert False
