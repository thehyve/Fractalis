"""This module provides tests for the transmart etl handler."""

import pytest
import responses
from fractalis import sync, app

from fractalis.data.etls.transmart.handler_transmart import TransmartHandler


# noinspection PyMissingOrEmptyDocstring,PyMissingTypeHints
class TestTransmartHandler:

    @pytest.fixture(scope='function')
    def test_client(self):
        sync.cleanup_all()
        from fractalis import app
        app.testing = True
        with app.test_client() as test_client:
            yield test_client
            sync.cleanup_all()

    @pytest.fixture(scope='function', params=[
        {'server': 'http://foo.bar', 'auth': ''},
        {'server': 'http://foo.bar', 'auth': {}},
        {'server': 'http://foo.bar', 'auth': {'abc': 'abc'}},
        {'server': 'http://foo.bar', 'auth': {'token': ''}},
        {'server': 'http://foo.bar', 'auth': {'token': object}},
        {'server': '', 'auth': {'token': 'foo'}},
        {'server': object, 'auth': {'token': 'foo'}},
        {'server': 'http://foo.bar', 'auth': {'user': 'foo', 'passwd': 'bar'}}
    ])
    def bad_init_args(self, request):
        return request.param

    def test_throws_if_bad_init_args(self, bad_init_args):
        with pytest.raises(ValueError):
            TransmartHandler(**bad_init_args)

    def test_returns_token_for_credentials(self, test_client):
        app.config['OIDC_OFFLINE_TOKEN'] = ''
        tmh = TransmartHandler(server='http://foo.bar',
                               auth={'token': 'foo-token'})
        assert tmh._token == 'foo-token'

    def test_returns_refreshed_token_for_credentials(self, test_client):
        app.config['OIDC_OFFLINE_TOKEN'] = 'test-offline-token'
        app.config['OIDC_CLIENT_ID'] = 'test_client'
        app.config['OIDC_SERVER_URL'] = 'http://foo.bar.oidc/auth/realms/transmart-realm/'
        with app.app_context():
            app.config['OIDC_OFFLINE_TOKEN'] = 'test-offline-token'

            token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkZvbyBVc2VyIiwiaWF0Ijox' \
                    'NTE2MjM5MDIyfQ.plmbGfh0j8xVCK4rM3pAuadj9Z5XPS33OAqkSx3Tt9s'
            with responses.RequestsMock() as response:
                response.add(response.POST, 'http://foo.bar.oidc/auth/realms/transmart-realm/protocol/openid-connect/token',
                             body='{"grant_type": "refresh_token", '
                                  '"scope": "offline_access", "client_id": "test_client", '
                                  '"refresh_token": "test-offline-token"}',
                             status=200,
                             content_type='application/json')
                response.add(response.POST, 'http://foo.bar.oidc/auth/realms/transmart-realm/protocol/openid-connect/token',
                             body='{"grant_type": "urn:ietf:params:oauth:grant-type:token-exchange", '
                                  '"requested_subject": "1234567890", "client_id": "test_client", '
                                  '"subject_token": "test-offline-token"}',
                             status=200,
                             content_type='application/json')
                tmh = TransmartHandler(server='http://foo.bar',
                                       auth={'token': token})
                assert tmh._token == token

    def test_auth_raises_exception_for_non_json_return(self):
        app.config['OIDC_OFFLINE_TOKEN'] = 'test-offline-token'
        app.config['OIDC_CLIENT_ID'] = 'test_client'
        app.config['OIDC_SERVER_URL'] = 'http://foo.bar.oidc/auth/realms/transmart-realm/'
        with responses.RequestsMock() as response:
            response.add(response.POST, 'http://foo.bar.oidc/auth/realms/transmart-realm/protocol/openid-connect/token',
                         body='123{//}',
                         status=200,
                         content_type='application/json')
            # with pytest.raises(ValueError) as e:
            e = TransmartHandler(server='http://foo.bar',
                             auth={'token': 'foo-token'})
            assert 'unexpected response' in str(e)

    def test_auth_raises_exception_for_non_200_return(self):
        app.config['OIDC_OFFLINE_TOKEN'] = 'test-offline-token'
        app.config['OIDC_CLIENT_ID'] = 'test_client'
        app.config['OIDC_SERVER_URL'] = 'http://foo.bar.oidc/auth/realms/transmart-realm/'
        with responses.RequestsMock() as response:
            response.add(response.POST, 'http://foo.bar.oidc/auth/realms/transmart-realm/protocol/openid-connect/token',
                         body='something',
                         status=400,
                         content_type='application/json')
            with pytest.raises(ValueError) as e:
                TransmartHandler(server='http://foo.bar',
                                 auth={'token': 'foo-token'})
            assert '[400]' in str(e.value)

