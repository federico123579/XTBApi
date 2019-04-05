"""
tests.test_client.py
~~~~~~~

test the api client
"""

import logging

import pytest

from XTBApi.api import Client

LOGGER = logging.getLogger('XTBApi.test_client')

USERID = '10649413'
PASSWORD = '***REMOVED***'
DEFAULT_CURRENCY = 'EURUSD'


@pytest.fixture(scope="module")
def _get_client():
    return Client()


def test_login(_get_client):
    client = _get_client
    response = client.login(USERID, PASSWORD)
    LOGGER.debug("passed")


def test_trades(_get_client):
    client = _get_client
    trades = client.update_trades()
    LOGGER.debug(trades)
    LOGGER.debug("passed")


# def test_profit(_get_client):
#     client = _get_client
#     # TODO
#     trade_id = client.get_trades()[]
#     trades = client.get_trade_profit()
#     LOGGER.debug("passed")


# at the end of file
def test_logout(_get_client):
    client = _get_client
    response = client.logout()
    LOGGER.debug("passed")
