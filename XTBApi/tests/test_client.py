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
    client.login(USERID, PASSWORD)
    LOGGER.debug("passed")


def test_trades(_get_client):
    client = _get_client
    trades = client.update_trades()
    LOGGER.debug(trades)
    LOGGER.debug("passed")


def test_trade_open(_get_client):
    client = _get_client
    trade_id = client.open_trade(0, 'EURUSD', 0.1)
    LOGGER.debug(trade_id)
    client.updates_trades()
    LOGGER.debug("passed")


def test_profit(_get_client):
    client = _get_client
    trade_id = client.get_trades()[0]
    trade_profit = client.get_trade_profit(trade_id)
    LOGGER.debug(trade_profit)
    LOGGER.debug("passed")


def test_close_trade(_get_client):
    client = _get_client
    trade_id = client.get_trades()[0]
    client.close_trade(trade_id)
    LOGGER.debug("passed")


# at the end of file
def test_logout(_get_client):
    client = _get_client
    client.logout()
    LOGGER.debug("passed")
