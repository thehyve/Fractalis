"""This module tests the data controller module."""

import json
import os
from uuid import UUID, uuid4

import flask
import pytest

from fractalis import app
from fractalis import redis
from fractalis import sync


class TestData:

    @pytest.fixture(scope='function')
    def test_client(self):
        sync.cleanup_all()
        from fractalis import app
        app.testing = True
        with app.test_client() as test_client:
            yield test_client
            sync.cleanup_all()

    @pytest.fixture(scope='function')
    def small_post(self, test_client):
        return lambda random: test_client.post(
            '/data', data=flask.json.dumps(dict(
                handler='test',
                server='localhost:1234',
                token='7746391376142672192764',
                descriptors=[
                    {
                        'data_type': 'foo',
                        'concept': str(uuid4()) if random else 'concept'
                    }
                ]
            )))

    @pytest.fixture(scope='function')
    def big_post(self, test_client):
        return lambda random: test_client.post(
            '/data', data=flask.json.dumps(dict(
                handler='test',
                server='localhost:1234',
                token='7746391376142672192764',
                descriptors=[
                    {
                        'data_type': 'foo',
                        'concept': str(uuid4()) if random else 'concept1'
                    },
                    {
                        'data_type': 'bar',
                        'concept': str(uuid4()) if random else 'concept2'
                    },
                    {
                        'data_type': 'foo',
                        'concept': str(uuid4()) if random else 'concept3'
                    },
                ]
            )))

    @pytest.fixture(scope='function', params=[
        {
            'handler': '',
            'server': 'localhost',
            'token': '1234567890',
            'descriptors': '[{"data_type": "foo", "concept": "GSE1234"}]'
        },
        {
            'handler': 'test',
            'server': '',
            'token': '1234567890',
            'descriptors': '[{"data_type": "foo", "concept": "GSE1234"}]'
        },
        {
            'handler': 'test',
            'server': 'localhost',
            'token': '',
            'descriptors': '[{"data_type": "foo", "concept": "GSE1234"}]'
        },
        {
            'handler': 'test',
            'server': 'localhost',
            'token': '1234567890',
            'descriptors': ''
        },
        {
            'handler': 'test',
            'server': 'localhost',
            'token': '1234567890',
            'descriptors': '[{"data_type": "foo", "concept": "GSE1234"}]'
        },
        {
            'handler': 'test',
            'server': 'localhost',
            'token': '1234567890',
            'descriptors': '[{"concept": "GSE1234"}]'
        },
        {
            'handler': 'test',
            'server': 'localhost',
            'token': '1234567890',
            'descriptors': '[{"data_type": "foo"}]'
        },
        {
            'handler': 'test',
            'server': 'localhost',
            'token': '1234567890',
            'descriptors': '[{"data_type": "", "concept": "GSE1234"}]'
        },
        {
            'handler': 'test',
            'server': 'localhost',
            'token': '1234567890',
            'descriptors': '[]'
        }
    ])
    def bad_post(self, test_client, request):
        return lambda: test_client.post('/data', data=flask.json.dumps(dict(
                handler=request.param['handler'],
                server=request.param['server'],
                token=request.param['token'],
                descriptors=request.param['descriptors']
            )))

    def test_bad_POST(self, bad_post):
        assert bad_post().status_code == 400

    def test_201_on_small_POST_and_valid_state(self, test_client, small_post):
        rv = small_post(random=False)
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 201, body
        assert len(body['data_ids']) == 1
        assert test_client.head('/data?wait=1').status_code == 200
        data_dir = os.path.join(app.config['FRACTALIS_TMP_DIR'], 'data')
        assert len(os.listdir(data_dir)) == 1
        assert UUID(os.listdir(data_dir)[0])
        data = redis.hgetall(name='data')
        assert len(data) == 1
        for key in data:
            data_obj = json.loads(data[key].decode('utf-8'))
            assert data_obj['job_id']
            assert data_obj['file_path']

    def test_201_on_big_POST_and_valid_state(self, test_client, big_post):
        rv = big_post(random=False)
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 201, body
        assert len(body['data_ids']) == 3
        assert test_client.head('/data?wait=1').status_code == 200
        data_dir = os.path.join(app.config['FRACTALIS_TMP_DIR'], 'data')
        assert len(os.listdir(data_dir)) == 3
        for f in os.listdir(data_dir):
            assert UUID(f)
        data = redis.hgetall(name='data')
        assert len(data) == 3
        for key in data:
            data_obj = json.loads(data[key].decode('utf-8'))
            assert data_obj['job_id']
            assert data_obj['file_path']

    def test_many_small_POST_and_valid_state(self, test_client, small_post):
        N = 10
        data_dir = os.path.join(app.config['FRACTALIS_TMP_DIR'], 'data')
        for i in range(N):
            rv = small_post(random=False)
            assert rv.status_code == 201
            body = flask.json.loads(rv.get_data())
            assert len(body['data_ids']) == 1
        assert test_client.head('/data?wait=1').status_code == 200
        assert len(os.listdir(data_dir)) == 1
        for f in os.listdir(data_dir):
            assert UUID(f)
        data = redis.hgetall(name='data')
        assert len(data) == 1
        for key in data:
            data_obj = json.loads(data[key].decode('utf-8'))
            assert data_obj['job_id']
            assert data_obj['file_path']

    def test_many_small_random_POST_and_valid_state(
            self, test_client, small_post):
        N = 10
        data_dir = os.path.join(app.config['FRACTALIS_TMP_DIR'], 'data')
        for i in range(N):
            rv = small_post(random=True)
            assert rv.status_code == 201
            body = flask.json.loads(rv.get_data())
            assert len(body['data_ids']) == 1
        assert test_client.head('/data?wait=1').status_code == 200
        assert len(os.listdir(data_dir)) == N
        for f in os.listdir(data_dir):
            assert UUID(f)
        data = redis.hgetall(name='data')
        assert len(data) == N
        for key in data:
            data_obj = json.loads(data[key].decode('utf-8'))
            assert data_obj['job_id']
            assert data_obj['file_path']

    def test_many_big_POST_and_valid_state(self, test_client, big_post):
        N = 10
        data_dir = os.path.join(app.config['FRACTALIS_TMP_DIR'], 'data')
        for i in range(N):
            rv = big_post(random=False)
            assert rv.status_code == 201
            body = flask.json.loads(rv.get_data())
            assert len(body['data_ids']) == 3
        assert test_client.head('/data?wait=1').status_code == 200
        assert len(os.listdir(data_dir)) == 3
        for f in os.listdir(data_dir):
            assert UUID(f)
        data = redis.hgetall(name='data')
        assert len(data) == 3
        for key in data:
            data_obj = json.loads(data[key].decode('utf-8'))
            assert data_obj['job_id']
            assert data_obj['file_path']

    def test_many_big_random_POST_and_valid_state(self, test_client, big_post):
        N = 10
        data_dir = os.path.join(app.config['FRACTALIS_TMP_DIR'], 'data')
        for i in range(N):
            rv = big_post(random=True)
            assert rv.status_code == 201
            body = flask.json.loads(rv.get_data())
            assert len(body['data_ids']) == 3
        assert test_client.head('/data?wait=1').status_code == 200
        assert len(os.listdir(data_dir)) == 3 * N
        for f in os.listdir(data_dir):
            assert UUID(f)
        data = redis.hgetall(name='data')
        assert len(data) == 3 * N
        for key in data:
            data_obj = json.loads(data[key].decode('utf-8'))
            assert data_obj['job_id']
            assert data_obj['file_path']

    def test_GET_by_id_and_valid_response(self, test_client, big_post):
        rv = big_post(random=False)
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 201, body
        data_ids = body['data_ids']
        assert len(data_ids) == 3
        for data_id in data_ids:
            rv = test_client.get('/data/{}'.format(data_id))
            body = flask.json.loads(rv.get_data())
            assert rv.status_code == 200, body
            assert len(body) == 3  # include only minimal data in response
            assert not body['message']
            assert body['state']
            assert body['job_id']

    def test_GET_by_all_and_valid_response(self, test_client, big_post):
        rv = big_post(random=False)
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 201, body
        data_ids = body['data_ids']
        assert len(data_ids) == 3

        rv = test_client.get('/data')
        body = flask.json.loads(rv.get_data())

        for data_state in body:
            assert len(data_state) == 3
            assert not data_state['message']
            assert data_state['state']
            assert data_state['job_id']

    def test_GET_by_params_and_valid_response(self, test_client):
        data = dict(
            handler='test',
            server='localhost:1234',
            token='7746391376142672192764',
            descriptors=[
                {
                    'data_type': 'foo',
                    'concept': str(uuid4())
                }
            ]
        )
        rv = test_client.post('/data', data=flask.json.dumps(data))
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 201, body
        payload = flask.json.dumps(dict(server=data['server'],
                                        descriptor=data['descriptors'][0]))
        rv = test_client.get('/data/{}'.format(payload))
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 200, body
        assert len(body) == 3  # include only minimal data in response
        assert not body['message']
        assert body['state']
        assert body['job_id']

    def test_404_on_GET_by_id_if_no_auth(self, test_client, big_post):
        rv = big_post(random=False)
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 201, body
        data_ids = body['data_ids']
        assert len(data_ids) == 3

        with test_client.session_transaction() as sess:
            sess['data_ids'].remove(data_ids[2])

        rv = test_client.get('/data/{}'.format(data_ids[0]))
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 200, body

        rv = test_client.get('/data/{}'.format(data_ids[1]))
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 200, body

        rv = test_client.get('/data/{}'.format(data_ids[2]))
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 404, body

    def test_404_on_GET_by_params_if_no_auth(self, test_client):
        data = dict(
            handler='test',
            server='localhost:1234',
            token='7746391376142672192764',
            descriptors=[
                {
                    'data_type': 'foo',
                    'concept': str(uuid4())
                }
            ]
        )
        rv = test_client.post('/data', data=flask.json.dumps(data))
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 201, body

        with test_client.session_transaction() as sess:
            sess['data_ids'] = []

        payload = flask.json.dumps(dict(server=data['server'],
                                        descriptor=data['descriptors'][0]))
        rv = test_client.get('/data/{}'.format(payload))
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 404, body

    def test_empty_response_for_empty_session(self, test_client, small_post):
        rv = small_post(random=False)
        body = flask.json.loads(rv.get_data())
        assert rv.status_code == 201, body

        rv = test_client.get('/data')
        body = flask.json.loads(rv.get_data())
        assert body, body

        with test_client.session_transaction() as sess:
            sess['data_ids'] = []

        rv = test_client.get('/data')
        body = flask.json.loads(rv.get_data())
        assert not body, body

    def test_exception_on_na_handler(self, test_client):
        data = dict(
            handler='abc',
            server='localhost:1234',
            token='7746391376142672192764',
            descriptors=[
                {
                    'data_type': 'foo',
                    'concept': str(uuid4())
                }
            ]
        )
        with pytest.raises(NotImplementedError):
            test_client.post('/data', data=flask.json.dumps(data))

    def test_exception_on_na_etl(self, test_client):
        data = dict(
            handler='test',
            server='localhost:1234',
            token='7746391376142672192764',
            descriptors=[
                {
                    'data_type': 'abc',
                    'concept': str(uuid4())
                }
            ]
        )
        with pytest.raises(NotImplementedError):
            test_client.post('/data', data=flask.json.dumps(data))