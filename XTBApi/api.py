# -*- coding utf-8 -*-

"""
XTBApi.api
~~~~~~~

Main module
"""

import json
import logging
import time

from websocket import create_connection

LOGGER = logging.getLogger('XTBApi.api')


def _get_data(command, **parameters):
    data = {
        "command": command,
    }
    if len(parameters) > 0:
        data['arguments'] = {}
        for key, value in parameters.items():
            data['arguments'][key] = value
    return data


class Client(object):
    """main client class"""

    def __init__(self):
        self.ws = create_connection("wss://ws.xapi.pro/demo")
        self.stream_ws = create_connection("wss://ws.xapi.pro/demoStream")
        self._stream_id = None
        self._time_last_request = 0

    def _send_command(self, dict_data):
        """send command to api"""
        time_interval = time.time() - self._time_last_request
        LOGGER.debug("took {} s.".format(time_interval))
        if time_interval < 0.200:
            time.sleep(0.200 - time_interval)
        self.ws.send(json.dumps(dict_data))
        response = self.ws.recv()
        self._time_last_request = time.time()
        return json.loads(response)

    def login(self, user_id, password):
        """login command"""
        data = _get_data("login", userId=user_id, password=password)
        response = self._send_command(data)
        self._stream_id = response['streamSessionId']
        return response

    def logout(self):
        """logout command"""
        data = _get_data("logout")
        return self._send_command(data)

    def get_all_symbols(self):
        """getAllSymbols command"""
        data = _get_data("getAllSymbols")
        return self._send_command(data)

    def get_calendar(self):
        """getCalendar command"""
        data = _get_data("getCalendar")
        return self._send_command(data)

    def get_chart_last_request(self, symbol, period, start):
        """getChartLastRequest command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        args = {
            "period": period,
            "start": start,
            "symbol": symbol
        }
        data = _get_data("getChartLastRequest", info=args)
        return self._send_command(data)

    def get_chart_range_request(self, symbol, period, start, end, ticks):
        """getChartRangeRequest command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        args = {
            "end": end,
            "period": period,
            "start": start,
            "symbol": symbol,
            "ticks": ticks
        }
        data = _get_data("getChartRangeRequest", info=args)
        return self._send_command(data)

    def get_commission(self, symbol, vol):
        """getCommissionDef command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("getCommissionDef", symbol=symbol, volume=vol)
        return self._send_command(data)

    def get_margin_level(self):
        """getMarginLevel command
        get margin information"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("getMarginLevel")
        return self._send_command(data)

    def get_margin_trade(self, symbol, volume):
        """getMarginTrade command
        get expected margin for volumes used symbol"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("getMarginTrade", symbol=symbol, volume=volume)
        return self._send_command(data)

    def get_profit_calculation(self, symbol, mode, vol, op_price, cl_price):
        """getProfitCalculation command
        get profit calculation for symbol with vol, mode and op, cl prices"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("getProfitCalculation", closePrice=cl_price,
                         cmd=mode, openPrice=op_price, symbol=symbol,
                         volume=vol)
        return self._send_command(data)

    def get_server_time(self):
        """getServerTime command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("getServerTime")
        return self._send_command(data)

    def get_symbol(self, symbol):
        """getSymbol command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("getSymbol", symbol=symbol)
        return self._send_command(data)

    def get_tick_prices(self, symbols, start, level=0):
        """getTickPrices command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("getTickPrices", level=level, symbols=symbols,
                         timestamp=start)
        return self._send_command(data)

    def get_trade_records(self, trade_position_list):
        """getTradeRecords command
        takes a list of position id"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("getTradeRecords", orders=trade_position_list)
        return self._send_command(data)

    def get_trades(self, opened_only=True):
        """getTrades command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("getTrades", openedOnly=opened_only)
        return self._send_command(data)

    def get_trades_history(self, start, end):
        """getTradesHistory command
        can take 0 as actual time"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("getTradesHistory", end=end, start=start)
        return self._send_command(data)

    def get_trading_hours(self, trade_position_list):
        """getTradingHours command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("getTradingHours", symbols=trade_position_list)
        return self._send_command(data)

    def get_version(self):
        """getVersion command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("getVersion")
        return self._send_command(data)

    def ping(self):
        """ping command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("ping")
        return self._send_command(data)

    def trade_transaction(self, symbol, mode, type, volume, order_id, price,
                         expiration, comment='', offset=0, sl=0, tp=0):
        """tradeTransaction command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        info = {
            'cmd': mode,
            'customComment': comment,
            'expiration': expiration,
            'offset': offset,
            'order': order_id,
            'price': price,
            'sl': sl,
            'symbol': symbol,
            'tp': tp,
            'type': type,
            'volume': volume
        }
        data = _get_data("tradeTransaction", tradeTransInfo=info)
        return self._send_command(data)

    def trade_transaction_status(self, pos_id):
        """tradeTransactionStatus command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        data = _get_data("tradeTransactionStatus", order=pos_id)
        return self._send_command(data)

    def get_user_data(self):
        """getCurrentUserData command"""
        data = _get_data("getCurrentUserData")
        return self._send_command(data)
