# Copyright (c) 2018 Intuit
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This module contains utility methods used by this library
"""

import json
import jwt
import random
import requests
import six
import string
from base64 import b64encode, b64decode
from datetime import datetime
from requests.sessions import Session
import secrets
import base64
import platform

from .enums import Scopes
from .exceptions import AuthClientError
from .version import __version__

# Platform information for user-agent
PYTHON_VERSION = platform.python_version()
OS_SYSTEM = platform.uname()[0]
OS_RELEASE_VER = platform.uname()[2]
OS_MACHINE = platform.uname()[4]

MIGRATION_URL = {
    'sandbox': 'https://developer-sandbox.api.intuit.com/v2/oauth2/tokens/migrate',
    'production': 'https://developer.api.intuit.com/v2/oauth2/tokens/migrate',
}

DISCOVERY_URL = {
    'sandbox': 'https://developer.intuit.com/.well-known/openid_sandbox_configuration/',
    'production': 'https://developer.intuit.com/.well-known/openid_configuration/',
}

ACCEPT_HEADER = {
    'Accept': 'application/json',
    'User-Agent': '{0}-{1}-{2}-{3} {4} {5} {6}'.format('Intuit-OAuthClient', __version__,'Python', PYTHON_VERSION, OS_SYSTEM, OS_RELEASE_VER, OS_MACHINE)
}

def get_discovery_doc(environment, session=None):
    """Get OpenID Connect discovery document"""
    if environment in ['sandbox', 'production', 'prod']:
        url = DISCOVERY_URL[environment]
        response = requests.get(url)
        return response.json()
    raise ValueError('Invalid environment specified')

def set_attributes(obj, response_json):
    """Sets attribute to an object from a dict
    
    :param obj: Object to set the attributes to
    :param response_json: dict with key names same as object attributes
    """

    for key in response_json:
        if key not in ['token_type', 'id_token']:
            setattr(obj, key, response_json[key])
    
    if 'id_token' in response_json:
        if response_json['id_token'] is not None:
            is_valid = validate_id_token(response_json['id_token'], obj.client_id, obj.issuer_uri, obj.jwks_uri)
            if is_valid:
                obj.id_token = response_json['id_token']  

def send_request(method, url, headers, client, body=None, session=None):
    """Send HTTP request and handle response"""
    if session:
        response = session.request(method, url, headers=headers, data=body)
    else:
        response = requests.request(method, url, headers=headers, data=body)
    
    if response.status_code != 200:
        raise Exception(f"Request failed with status {response.status_code}: {response.text}")
    
    return response

def get_auth_header(client_id, client_secret):
    """Generate Basic auth header"""
    credentials = f"{client_id}:{client_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"

def scopes_to_string(scopes):
    """Convert scope list to space-separated string"""
    return ' '.join(scope.value for scope in scopes)

def generate_token():
    """Generate a random token"""
    return secrets.token_urlsafe(32)

def validate_id_token(id_token, client_id, intuit_issuer, jwk_uri):
    """Validates ID Token returned by Intuit
    
    :param id_token: ID Token
    :param client_id: Client ID
    :param intuit_issuer: Intuit Issuer
    :param jwk_uri: JWK URI
    :return: True/False
    """

    id_token_parts = id_token.split('.')
    if len(id_token_parts) < 3:
        return False

    id_token_header = json.loads(b64decode(_correct_padding(id_token_parts[0])).decode('ascii'))
    id_token_payload = json.loads(b64decode(_correct_padding(id_token_parts[1])).decode('ascii'))

    if id_token_payload['iss'] != intuit_issuer:
        return False
    elif id_token_payload['aud'][0] != client_id:
        return False

    current_time = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
    if id_token_payload['exp'] < current_time:
        return False

    public_key = get_jwk(id_token_header['kid'], jwk_uri).key
    try:
        jwt.decode(id_token, public_key, audience=client_id, algorithms=['RS256'])
        return True
    except jwt.PyJWTError:
        return False

def get_jwk(kid, jwk_uri):
    """Get JWK for public key information
    
    :param kid: KID
    :param jwk_uri: JWK URI

    :raises HTTPError: if response status != 200
    :return: Algorithm with the key loaded.
    """

    response = requests.get(jwk_uri)
    if response.status_code != 200:
        raise AuthClientError(response)
    data = response.json()
    return jwt.PyJWKSet.from_dict(data)[kid]

def _correct_padding(val):
    """Correct padding for JWT
    
    :param val: value to correct
    """

    return val + '=' * (4 - len(val) % 4)