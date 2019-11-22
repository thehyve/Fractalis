"""This module provides TransmartHandler, an implementation of ETLHandler for
tranSMART."""

import logging
from typing import Dict

import jwt
import requests

from fractalis import app
from fractalis.data.etlhandler import ETLHandler


logger = logging.getLogger(__name__)


class TransmartHandler(ETLHandler):
    """This ETLHandler provides integration with tranSMART.

    'tranSMART is a knowledge management platform that enables scientists to
    develop and refine research hypotheses by investigating correlations
    between genetic and phenotypic data, and assessing their analytical results
    in the context of published literature and other work.'

    Project URL: https://github.com/transmart
    """

    _handler = 'transmart'

    @staticmethod
    def make_label(descriptor: dict) -> str:
        return descriptor['label']

    @staticmethod
    def get_auth_value(auth: dict, property_name: str) -> str:
        value = auth.get(property_name, '')
        if len(value) == 0:
            raise KeyError(f'The authentication object must contain the non-empty field: "{property_name}"')
        return value

    @staticmethod
    def get_access_token(url: str, params: Dict) -> str:
        """
        Get access token from authorization server
        :param url: authorization server URL
        :param params: request body params
        :return: access token
        """
        response = requests.post(url=url, data=params, headers={'Accept': 'application/json'})
        if not response.ok:
            error = "Could not get a token from OIDC server. " \
                    "Reason: [{}]: {}".format(response.status_code, response.text)
            logger.error(error)
            raise ValueError(error)
        try:
            json_response = response.json()
            return json_response['access_token']
        except Exception:
            error = "Could not retrieve the access token from {}. " \
                    "Got unexpected response: '{}'".format(url, response.text)
            logger.error(error)
            raise ValueError(error)

    @staticmethod
    def get_access_token_by_offline_token(offline_token: str, url: str, client_id: str) -> str:
        """
        Get access token based on offline token
        :return: offline user's access token
        """
        handle = f'{url}/protocol/openid-connect/token'
        params = {'grant_type': 'refresh_token',
                  'scope': 'offline_access',
                  'client_id': f'{client_id}',
                  'refresh_token': f'{offline_token}'}
        return TransmartHandler.get_access_token(handle, params)

    @staticmethod
    def exchange_offline_token_for_user_token(offline_token: str, user: str) -> str:
        """
        Exchange offline token to user access token using impersonation
        :param offline_token: offline token acting as a refresh token
        :param user: current user
        :return: current user's access token
        """
        try:
            client_id = app.config.get('OIDC_CLIENT_ID')
            url = app.config.get('OIDC_SERVER_URL')
            offline_user_access_token = TransmartHandler.get_access_token_by_offline_token(
                offline_token, url, client_id)
            handle = f'{url}/protocol/openid-connect/token'
            params = {'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
                      'requested_subject': user,
                      'client_id': f'{client_id}',
                      'subject_token': offline_user_access_token}
            return TransmartHandler.get_access_token(handle, params)
        except KeyError as e:
            logger.error(e)
            raise ValueError(e)

    def _get_token_for_credentials(self, server: str, auth: dict) -> str:
        token = TransmartHandler.get_auth_value(auth, 'token')
        if token and len(token) > 0:
            offline_token = app.config.get('OIDC_OFFLINE_TOKEN', '')
            if offline_token and len(offline_token) > 0:
                decoded_token = jwt.decode(token, verify=False)
                user = decoded_token.get('sub')
                return self.exchange_offline_token_for_user_token(offline_token, user)
            else:
                return token
        raise ValueError("No token in the authentication object.")

