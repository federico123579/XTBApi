"""
tests.test_base_client.py
~~~~~~~

test the api client
"""

import logging
import time

import pytest

from XTBApi.api import BaseClient

LOGGER = logging.getLogger('XTBApi.test_base_client')

USERID = '10649413'
PASSWORD = '20072001FdRcLlL'
DEFAULT_CURRENCY = 'EURUSD'


@pytest.fixture(scope="module")
def _get_client():
    return BaseClient()


def test_login(_get_client):
    client = _get_client
    response = client.login(USERID, PASSWORD)
    LOGGER.debug("passed")


def test_all_symbols(_get_client):
    client = _get_client
    response = client.get_all_symbols()
    LOGGER.debug("passed")


def test_get_calendar(_get_client):
    client = _get_client
    response = client.get_calendar()
    LOGGER.debug("passed")


def test_get_chart_last_request(_get_client):
    client = _get_client
    start = (time.time() - 3600*24) * 1000
    args = [DEFAULT_CURRENCY, 1440, start]
    response = client.get_chart_last_request(*args)
    LOGGER.debug("passed")


def test_get_chart_range_request(_get_client):
    client = _get_client
    start = (time.time() - 3600*24*2) * 1000
    end = (time.time() - 3600*24) * 1000
    args = [DEFAULT_CURRENCY, 1440, start, end, 0]
    response = client.get_chart_range_request(*args)
    LOGGER.debug("passed")


def test_get_commission(_get_client):
    client = _get_client
    response = client.get_commission(DEFAULT_CURRENCY, 1.0)
    LOGGER.debug("passed")


def test_get_user_data(_get_client):
    client = _get_client
    response = client.get_user_data()
    LOGGER.debug("passed")


def test_get_margin_level(_get_client):
    client = _get_client
    response = client.get_margin_level()
    LOGGER.debug("passed")


def test_get_margin_trade(_get_client):
    client = _get_client
    response = client.get_margin_trade(DEFAULT_CURRENCY, 1.0)
    LOGGER.debug("passed")


def test_get_profit_calculation(_get_client):
    client = _get_client
    args = [DEFAULT_CURRENCY, 0, 1.0, 1.2233, 1.3000]
    response = client.get_profit_calculation(*args)
    LOGGER.debug("passed")


def test_get_server_time(_get_client):
    client = _get_client
    response = client.get_server_time()
    LOGGER.debug("passed")


def test_symbol(_get_client):
    client = _get_client
    response = client.get_symbol(DEFAULT_CURRENCY)
    LOGGER.debug("passed")


def test_get_tick_prices(_get_client):
    client = _get_client
    args = [[DEFAULT_CURRENCY], time.time() - 3600*24, 0]
    response = client.get_tick_prices(*args)
    LOGGER.debug("passed")


def test_get_trade_records(_get_client):
    client = _get_client
    response = client.get_trade_records([7489839])
    LOGGER.debug("passed")


def test_get_trades(_get_client):
    client = _get_client
    response = client.get_trades(True)
    LOGGER.debug("passed")


def test_get_trades_history(_get_client):
    client = _get_client
    args = [time.time() - 3600*24, 0]
    response = client.get_trades_history(*args)
    LOGGER.debug("passed")


def test_get_trading_hours(_get_client):
    client = _get_client
    response = client.get_trading_hours([DEFAULT_CURRENCY])
    LOGGER.debug("passed")


def test_get_version(_get_client):
    client = _get_client
    response = client.get_version()
    LOGGER.debug("passed")


def test_ping(_get_client):
    client = _get_client
    response = client.ping()
    LOGGER.debug("passed")


def test_trade_transaction(_get_client):
    client = _get_client
    price = client.get_symbol(DEFAULT_CURRENCY)['ask']
    args = [DEFAULT_CURRENCY, 0, 0, 5.0, 0, price, 0]
    response = client.trade_transaction(*args)
    LOGGER.debug("passed")


def test_trade_transaction_status(_get_client):
    client = _get_client
    price = client.get_symbol(DEFAULT_CURRENCY)['ask']
    args = [DEFAULT_CURRENCY, 0, 0, 5.0, 0, price, 0]
    pos_id = client.trade_transaction(*args)['order']
    response = client.trade_transaction_status(pos_id)
    LOGGER.debug("passed")


# at the end of file
def test_logout(_get_client):
    client = _get_client
    response = client.logout()
    LOGGER.debug("passed")
