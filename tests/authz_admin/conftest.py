import time

import pytest
import jwt

from authz_admin.config import load as load_config
from authz_admin.main import build_application

from authorization_django import jwks


@pytest.fixture()
def client(loop, test_client):
    """An aiohttp test_client initialized for our app."""
    return loop.run_until_complete(test_client(build_application()))


@pytest.fixture()
def base_path(client):
    return client.server.app['swagger'].base_path


@pytest.fixture(scope='session')
def aaconfig():
    # language=rst
    """Fixture that gives access to a loaded configuration file."""
    return load_config()


@pytest.fixture(scope='session')
def api_key(aaconfig) -> str:
    return aaconfig['authz_admin']['api_key']


@pytest.fixture(scope='session')
def access_token(aaconfig) -> str:
    # language=rst
    """Fixture that gives a valid access token to use."""

    jwks_string = aaconfig['authz_admin']['jwks']
    jwks_signers = jwks.load(jwks_string).signers

    assert len(jwks_signers) > 0

    list_signers = [(k, v) for k, v in jwks_signers.items()]
    (kid, key) = list_signers[len(list_signers) - 1]
    header = {"kid": kid}

    now = int(time.time())
    token_dict = {
        'iat': now,
        'exp': now + 3600 * 12,
        'scopes': ['AUR/R', 'AUR/W'],
    }
    return jwt.encode(
        token_dict,
        key=key.key,
        algorithm=key.alg,
        headers=header
    ).decode()
