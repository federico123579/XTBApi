# -*- coding utf-8 -*-

"""
XTBApi.api
~~~~~~~

Main module
"""

import json
import time
from enum import auto, Enum

from websocket import create_connection

from XTBApi.exceptions import *

LOGGER = logging.getLogger('XTBApi.api')
LOGIN_TIMEOUT = 600
MAX_TIME_INTERVAL = 0.200


class STATUS(Enum):
    LOGGED = auto()
    NOT_LOGGED = auto()


class MODES(Enum):
    BUY = 0
    SELL = 1


def _get_data(command, **parameters):
    data = {
        "command": command,
    }
    if parameters:
        data['arguments'] = {}
        for key, value in parameters.items():
            data['arguments'][key] = value
    return data


class BaseClient(object):
    """main client class"""

    def __init__(self):
        self.ws = None
        self._login_data = None
        self._time_last_request = time.time() - MAX_TIME_INTERVAL
        self.status = STATUS.NOT_LOGGED

    def _send_command(self, dict_data):
        """send command to api"""
        time_interval = time.time() - self._time_last_request
        LOGGER.debug("took {} s.".format(time_interval))
        if time_interval < MAX_TIME_INTERVAL:
            time.sleep(MAX_TIME_INTERVAL - time_interval)
        self.ws.send(json.dumps(dict_data))
        response = self.ws.recv()
        self._time_last_request = time.time()
        res = json.loads(response)
        if res['status'] is False:
            raise CommandFailed(res)
        if 'returnData' in res.keys():
            return res['returnData']

    def _check_login(self):
        if self.status == STATUS.NOT_LOGGED:
            raise NotLogged()
        elif time.time() - self._time_last_request >= LOGIN_TIMEOUT:
            self.login(self._login_data[0], self._login_data[1])


    def login(self, user_id, password):
        """login command"""
        data = _get_data("login", userId=user_id, password=password)
        self.ws = create_connection("wss://ws.xapi.pro/demo")
        response = self._send_command(data)
        self._login_data = (user_id, password)
        self.status = STATUS.LOGGED
        return response

    def logout(self):
        """logout command"""
        data = _get_data("logout")
        return self._send_command(data)

    def get_all_symbols(self):
        """getAllSymbols command"""
        self._check_login()
        data = _get_data("getAllSymbols")
        return self._send_command(data)

    def get_calendar(self):
        """getCalendar command"""
        self._check_login()
        data = _get_data("getCalendar")
        return self._send_command(data)

    def get_chart_last_request(self, symbol, period, start):
        """getChartLastRequest command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        self._check_login()
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
        self._check_login()
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
        self._check_login()
        data = _get_data("getCommissionDef", symbol=symbol, volume=vol)
        return self._send_command(data)

    def get_margin_level(self):
        """getMarginLevel command
        get margin information"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
        data = _get_data("getMarginLevel")
        return self._send_command(data)

    def get_margin_trade(self, symbol, volume):
        """getMarginTrade command
        get expected margin for volumes used symbol"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
        data = _get_data("getMarginTrade", symbol=symbol, volume=volume)
        return self._send_command(data)

    def get_profit_calculation(self, symbol, mode, vol, op_price, cl_price):
        """getProfitCalculation command
        get profit calculation for symbol with vol, mode and op, cl prices"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
        data = _get_data("getProfitCalculation", closePrice=cl_price,
                         cmd=mode, openPrice=op_price, symbol=symbol,
                         volume=vol)
        return self._send_command(data)

    def get_server_time(self):
        """getServerTime command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
        data = _get_data("getServerTime")
        return self._send_command(data)

    def get_symbol(self, symbol):
        """getSymbol command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
        data = _get_data("getSymbol", symbol=symbol)
        return self._send_command(data)

    def get_tick_prices(self, symbols, start, level=0):
        """getTickPrices command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
        data = _get_data("getTickPrices", level=level, symbols=symbols,
                         timestamp=start)
        return self._send_command(data)

    def get_trade_records(self, trade_position_list):
        """getTradeRecords command
        takes a list of position id"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
        data = _get_data("getTradeRecords", orders=trade_position_list)
        return self._send_command(data)

    def get_trades(self, opened_only=True):
        """getTrades command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
        data = _get_data("getTrades", openedOnly=opened_only)
        return self._send_command(data)

    def get_trades_history(self, start, end):
        """getTradesHistory command
        can take 0 as actual time"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
        data = _get_data("getTradesHistory", end=end, start=start)
        return self._send_command(data)

    def get_trading_hours(self, trade_position_list):
        """getTradingHours command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
        data = _get_data("getTradingHours", symbols=trade_position_list)
        return self._send_command(data)

    def get_version(self):
        """getVersion command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
        data = _get_data("getVersion")
        return self._send_command(data)

    def ping(self):
        """ping command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
        data = _get_data("ping")
        return self._send_command(data)

    def trade_transaction(self, symbol, mode, type, volume, order_id=0, price=0,
                         expiration=0, comment='', offset=0, sl=0, tp=0):
        """tradeTransaction command"""
        # TODO: add exception handling
        # TODO: add parameters value check
        # TODO: add accepted parameters
        self._check_login()
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
        self._check_login()
        data = _get_data("tradeTransactionStatus", order=pos_id)
        return self._send_command(data)

    def get_user_data(self):
        """getCurrentUserData command"""
        self._check_login()
        data = _get_data("getCurrentUserData")
        return self._send_command(data)


class Transaction(object):
    def __init__(self, trans_dict):
        self._trans_dict = trans_dict
        self.id = trans_dict['order']
        self.symbol = trans_dict['symbol']
        self.closed = trans_dict['closed']
        self.volume = trans_dict['volume']
        self.actual_profit = trans_dict['profit']


class Client(BaseClient):
    """advanced class of client"""
    def __init__(self):
        super().__init__()
        self.trade_rec = {}

    def update_trades(self):
        """update trans list"""
        data = self.get_trades()
        for trade in data:
            obj_trans = Transaction(trade)
            self.trade_rec[obj_trans.id] = obj_trans
        return self.trade_rec

    def get_trade_profit(self, trans_id):
        """get profit of trade"""
        self.update_trades()
        return self.trade_rec[trans_id].actual_profit

    def open_trade(self, mode, symbol, volume):
        """open trade transaction"""
        if mode not in ['buy', 'ask']:
            raise ValueError("mode can be buy or sell")
        modes = {'buy': MODES.BUY, 'ask': MODES.SELL}
        self.trade_transaction(symbol, modes[mode], 0, volume)

