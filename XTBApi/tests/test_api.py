"""
tests.test_api.py
~~~~~~~

test the api client
"""

import pytest

from XTBApi.api import Client


@pytest.fixture(scope="module")
def _get_client():
    return Client()


def test_login(_get_client):
    client = _get_client
    response = client.login('10649413', '***REMOVED***')
    print(response)
    print(response)
    assert response['status'] is True
    assert client._stream_id is not None


def test_get_balance(_get_client):
    client = _get_client
    response = client.get_balance()
    print(response)
    assert response is not None


def test_get_candles(_get_client):
    client = _get_client
    response = client.get_candles('EURUSD')
    print(response)
    assert response is not None


def test_all_symbols(_get_client):
    client = _get_client
    response = client.get_all_symbols()
    print(response)
    assert response['status'] is True


def test_calendar(_get_client):
    client = _get_client
    response = client.get_calendar()
    print(response)
    assert response['status'] is True


def test_get_commission(_get_client):
    client = _get_client
    response = client.get_commission('EURUSD', 1.0)
    print(response)
    assert response['status'] is True


def test_get_user_data(_get_client):
    client = _get_client
    response = client.get_user_data()
    print(response)
    assert response['status'] is True


# at the end of file
def test_logout(_get_client):
    client = _get_client
    response = client.logout()
    print(response)
    assert response['status'] is True
