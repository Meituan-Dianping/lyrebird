from lyrebird.mock import data_manager
from pathlib import Path
import json
import codecs
import pytest


# @pytest.fixture
# def tmpdir():
#     return '/Users/zhaoye/work/tmp/gittest'


@pytest.fixture
def flow():
    mock_flow = {
        'request': {
            'url': 'http://www.test.com',
            'headers': {
                'Content-Type': 'text/html'
            },
            'method': 'POST',
            'data': 'REQUEST-DATA'
            }, 
        'response': {
            'code': 200,
            'headers': {
                'Content-Type': 'text/html'
            },
            'data': 'RESPONSE-DATA'
            }
        }
    return mock_flow


@pytest.fixture
def dm_helper(tmpdir, flow):
    def create(group_num=1, data_num=1):
        dm = data_manager.DataManager()
        dm.root = tmpdir
        for i in range(group_num):
            group = dm.create_group()
            group.name = f'G-{i}'
            group.save()
            for j in range(data_num):
                data = group.create_data(flow)
                data.name = f'D-{i}-{j}'
                data.save()
        return dm
    return create


def test_create_group(tmpdir):
    dm = data_manager.DataManager()
    dm.root = tmpdir
    groups_count = len(dm.groups)
    group = dm.create_group()
    assert len(dm.groups) == groups_count+1
    group.name = 'TestGroup-1'
    group.save()
    assert (Path(tmpdir)/group.id).exists()


def test_create_data(tmpdir, flow):
    dm = data_manager.DataManager()
    dm.root = tmpdir
    group = dm.create_group()
    group.name = 'TestGroup-1'
    group.save()

    data = group.create_data(flow)
    assert len(group.all_data) == 1
    data.save()
    assert Path(data.path).exists()


def test_load_data(tmpdir, flow):
    dm = data_manager.DataManager()
    dm.root = tmpdir
    group = dm.create_group()
    group.save()
    data_ids = []
    for _ in range(5):
        data = group.create_data(flow)
        data.save()
        data_ids.append(data.id)

    # new object
    dm = data_manager.DataManager()
    dm.root = tmpdir

    group_1 = dm.groups.get(group.id)
    assert group_1.name == group.name
    assert len(group_1.all_data) == 5
    for _id in group_1.all_data:
        assert _id in data_ids


def test_activate_group(dm_helper):
    dm = dm_helper()
    gid = list(dm.groups.keys())[0]
    dm.activate(gid)

    assert dm.activated_group_id == gid
