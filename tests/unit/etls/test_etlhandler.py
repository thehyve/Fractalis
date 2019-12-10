"""This module provides tests for the etlhandler module."""

import os
from pathlib import Path

import pytest

from fractalis import celery, app, DataServices
from fractalis.data.etlhandler import ETLHandler


# noinspection PyMissingOrEmptyDocstring,PyMissingTypeHints,PyPep8Naming
from fractalis.data.etls.test.handler_test import TestHandler
from fractalis.data_services_config import DataService


class TestETLHandler:

    @pytest.fixture(scope='class')
    def data_services_config(self):
        return DataServices(
            data_services={'test-service': DataService(handler='test', server='localfoo')}
        )
    #
    # @pytest.fixture(scope='function')
    # def etlhandler(self, data_services_config):
    #     return ETLHandler.factory(service_name='test', auth={})

    @pytest.fixture(scope='function')
    def etlhandler(self):
        global data_services_config
        data_services_config = DataServices(
            data_services={'test-service': DataService(handler='test', server='localfoo')}
        )
        return ETLHandler.factory(service_name='test-service', auth={})

    @pytest.fixture(scope='function')
    def redis(self):
        from fractalis import redis, sync
        yield redis
        sync.cleanup_all()

    def test_descriptor_to_hash_produces_unique_hash(self, redis, etlhandler):
        hash_1 = etlhandler.descriptor_to_hash(descriptor={'a': 1})
        hash_2 = etlhandler.descriptor_to_hash(descriptor={'': ''})
        hash_3 = etlhandler.descriptor_to_hash(descriptor={'a': 1})
        etlhandler._server = 'localbar'
        hash_4 = etlhandler.descriptor_to_hash(descriptor={'a': 1})
        assert isinstance(hash_1, int)
        assert isinstance(hash_4, int)
        assert hash_1 == hash_3
        assert hash_1 != hash_2
        assert hash_1 != hash_4

    def test_find_duplicates_finds_duplicates_by_hash(self, redis, etlhandler):
        descriptor = {'a': {'b': 3}, 'c': 4}
        etlhandler.create_redis_entry(task_id='123',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')
        duplicates = etlhandler.find_duplicates(data_tasks=['123'],
                                                descriptor=descriptor)
        assert len(duplicates) == 1
        assert duplicates[0] == '123'

    def test_finds_all_duplicates(self, redis, etlhandler):
        descriptor = {'a': {'b': 3}, 'c': 4}
        etlhandler.create_redis_entry(task_id='123',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')
        etlhandler.create_redis_entry(task_id='456',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')
        etlhandler.create_redis_entry(task_id='789',
                                      file_path='',
                                      descriptor={'a': 5},
                                      data_type='')
        duplicates = etlhandler.find_duplicates(
            data_tasks=['123', '456', '789'], descriptor=descriptor)
        assert len(duplicates) == 2
        assert '123' in duplicates
        assert '456' in duplicates

    def test_find_duplicates_only_operates_on_given_list(self, redis, etlhandler):
        descriptor = {'a': {'b': 3}, 'c': 4}
        etlhandler.create_redis_entry(task_id='123',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')
        etlhandler.create_redis_entry(task_id='456',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')
        etlhandler.create_redis_entry(task_id='789',
                                      file_path='',
                                      descriptor={'a': 5},
                                      data_type='')
        duplicates = etlhandler.find_duplicates(
            data_tasks=['456', '789'], descriptor=descriptor)
        assert len(duplicates) == 1
        assert '456' in duplicates

    def test_remove_duplicates_removes_duplicate(self, redis, etlhandler):
        descriptor = {'a': {'b': 3}, 'c': 4}
        etlhandler.create_redis_entry(task_id='456',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')
        data_dir = os.path.join(app.config['FRACTALIS_TMP_DIR'], 'data')
        os.makedirs(data_dir, exist_ok=True)
        Path(os.path.join(data_dir, '456')).touch()
        assert redis.exists('data:456')
        etlhandler.remove_duplicates(data_tasks=['456'],
                                     descriptor=descriptor)
        assert not redis.exists('data:456')

    def test_remove_duplicates_removes_all_duplicates(self, redis, etlhandler):
        descriptor = {'a': {'b': 3}, 'c': 4}
        etlhandler.create_redis_entry(task_id='123',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')
        etlhandler.create_redis_entry(task_id='456',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')
        etlhandler.create_redis_entry(task_id='789',
                                      file_path='',
                                      descriptor={'a': 1},
                                      data_type='')
        data_dir = os.path.join(app.config['FRACTALIS_TMP_DIR'], 'data')
        os.makedirs(data_dir, exist_ok=True)
        Path(os.path.join(data_dir, '123')).touch()
        Path(os.path.join(data_dir, '456')).touch()
        Path(os.path.join(data_dir, '789')).touch()
        assert redis.exists('data:123')
        assert redis.exists('data:456')
        assert redis.exists('data:789')
        etlhandler.remove_duplicates(data_tasks=['123', '456', '789'],
                                     descriptor=descriptor)
        assert not redis.exists('data:123')
        assert not redis.exists('data:456')
        assert redis.exists('data:789')

    def test_remove_duplicates_only_operates_on_given_list(self, redis, etlhandler):
        descriptor = {'a': {'b': 3}, 'c': 4}
        etlhandler.create_redis_entry(task_id='123',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')
        etlhandler.create_redis_entry(task_id='456',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')
        etlhandler.create_redis_entry(task_id='789',
                                      file_path='',
                                      descriptor={'a': 1},
                                      data_type='')
        data_dir = os.path.join(app.config['FRACTALIS_TMP_DIR'], 'data')
        os.makedirs(data_dir, exist_ok=True)
        Path(os.path.join(data_dir, '123')).touch()
        Path(os.path.join(data_dir, '456')).touch()
        Path(os.path.join(data_dir, '789')).touch()
        assert redis.exists('data:123')
        assert redis.exists('data:456')
        assert redis.exists('data:789')
        etlhandler.remove_duplicates(data_tasks=['123', '789'],
                                     descriptor=descriptor)
        assert not redis.exists('data:123')
        assert redis.exists('data:456')
        assert redis.exists('data:789')

    def test_find_duplicate_task_id_returns_task_id_of_SUCCESS(
            self, monkeypatch, redis, etlhandler):
        descriptor = {'a': {'b': 3}, 'c': 4}
        etlhandler.create_redis_entry(task_id='123',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')

        class FakeAsyncResult:
            def __init__(self, *args, **kwargs):
                self.state = 'SUCCESS'

            def get(self, *args, **kwargs):
                pass

        monkeypatch.setattr(celery, 'AsyncResult', FakeAsyncResult)
        task_id = etlhandler.find_duplicate_task_id(
            data_tasks=['123'], descriptor=descriptor)
        assert task_id == '123'

    def test_find_duplicate_task_id_returns_task_id_of_SUBMITTED(
            self, monkeypatch, redis, etlhandler):
        descriptor = {'a': {'b': 3}, 'c': 4}
        etlhandler.create_redis_entry(task_id='123',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')

        class FakeAsyncResult:
            def __init__(self, *args, **kwargs):
                self.state = 'SUBMITTED'

            def get(self, *args, **kwargs):
                pass

        monkeypatch.setattr(celery, 'AsyncResult', FakeAsyncResult)
        task_id = etlhandler.find_duplicate_task_id(
            data_tasks=['123'], descriptor=descriptor)
        assert task_id == '123'

    def test_find_duplicate_task_id_returns_None_for_FAILURE(
            self, monkeypatch, redis, etlhandler):
        descriptor = {'a': {'b': 3}, 'c': 4}
        etlhandler.create_redis_entry(task_id='123',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')

        class FakeAsyncResult:
            def __init__(self, *args, **kwargs):
                self.state = 'FAILURE'

            def get(self, *args, **kwargs):
                pass

        monkeypatch.setattr(celery, 'AsyncResult', FakeAsyncResult)
        task_id = etlhandler.find_duplicate_task_id(
            data_tasks=['123'], descriptor=descriptor)
        assert task_id is None

    def test_find_duplicate_limits_search_to_data_tasks(
            self, monkeypatch, redis, etlhandler):
        descriptor = {'a': {'b': 3}, 'c': 4}
        etlhandler.create_redis_entry(task_id='123',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')

        class FakeAsyncResult:
            def __init__(self, *args, **kwargs):
                self.state = 'SUCCESS'

            def get(self, *args, **kwargs):
                pass

        monkeypatch.setattr(celery, 'AsyncResult', FakeAsyncResult)
        task_id = etlhandler.find_duplicate_task_id(
            data_tasks=['456'], descriptor=descriptor)
        assert task_id is None

    def test_find_duplicate_task_id_returns_None_for_not_existing(
            self, monkeypatch, redis, etlhandler):
        descriptor = {'a': {'b': 3}, 'c': 4}

        class FakeAsyncResult:
            def __init__(self, *args, **kwargs):
                self.state = 'FAILURE'

            def get(self, *args, **kwargs):
                pass

        monkeypatch.setattr(celery, 'AsyncResult', FakeAsyncResult)
        task_id = etlhandler.find_duplicate_task_id(
            data_tasks=['123'], descriptor=descriptor)
        assert task_id is None

    def test_handle_reuses_existing_task_ids_if_use_existing(
            self, monkeypatch, redis, etlhandler):
        descriptor = {'data_type': 'default'}
        etlhandler.create_redis_entry(task_id='123',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')

        class FakeAsyncResult:
            def __init__(self, *args, **kwargs):
                self.state = 'SUBMITTED'

            def get(self, *args, **kwargs):
                pass

        monkeypatch.setattr(celery, 'AsyncResult', FakeAsyncResult)
        task_ids = etlhandler.handle(descriptors=[descriptor],
                                     data_tasks=['123'],
                                     use_existing=True)
        assert len(task_ids) == 1
        assert task_ids[0] == '123'

    def test_handle_limits_search_to_tasks_ids(self, monkeypatch, redis, etlhandler):
        descriptor = {'data_type': 'default'}
        etlhandler.create_redis_entry(task_id='123',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')
        task_ids = etlhandler.handle(descriptors=[descriptor],
                                     data_tasks=[],
                                     use_existing=True)
        assert len(task_ids) == 1
        assert task_ids[0] != '123'

    def test_handle_removes_old_and_returns_new_if_not_use_existing(
            self, monkeypatch, redis, etlhandler):
        descriptor = {'data_type': 'default'}
        etlhandler.create_redis_entry(task_id='123',
                                      file_path='',
                                      descriptor=descriptor,
                                      data_type='')
        task_ids = etlhandler.handle(descriptors=[descriptor],
                                     data_tasks=['123'],
                                     use_existing=False)
        assert len(task_ids) == 1
        assert task_ids[0] != '123'

    def test_handle_removes_duplicate_of_previous_iteration(
            self, monkeypatch, redis, etlhandler):
        descriptor = {'data_type': 'default'}
        task_ids = etlhandler.handle(descriptors=[descriptor, descriptor],
                                     data_tasks=[],
                                     use_existing=False)
        assert len(task_ids) == 2
        assert task_ids[0] != task_ids[1]
        assert len(redis.keys('data:*')) == 1

    def test_handle_uses_duplicate_of_previous_iteration(
            self, monkeypatch, redis, etlhandler):
        descriptor = {'data_type': 'default'}
        task_ids = etlhandler.handle(descriptors=[descriptor, descriptor],
                                     data_tasks=[],
                                     use_existing=True)
        assert len(task_ids) == 1
        assert len(redis.keys('data:*')) == 1
