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
from websocket._exceptions import WebSocketConnectionClosedException

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
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    BUY_STOP = 4
    SELL_STOP = 5
    BALANCE = 6
    CREDIT = 7


class TRANS_TYPES(Enum):
    OPEN = 0
    PENDING = 1
    CLOSE = 2
    MODIFY = 3
    DELETE = 4


class PERIOD(Enum):
    ONE_MINUTE = 1
    FIVE_MINUTES = 5
    FIFTEEN_MINUTES = 15
    THIRTY_MINUTES = 30
    ONE_HOUR = 60
    FOUR_HOURS = 240
    ONE_DAY = 1440
    ONE_WEEK = 10080
    ONE_MONTH = 43200


def _get_data(command, **parameters):
    data = {
        "command": command,
    }
    if parameters:
        data['arguments'] = {}
        for key, value in parameters.items():
            data['arguments'][key] = value
    return data


def _check_mode(mode):
    """check if mode acceptable"""
    modes = [x.value for x in MODES]
    if mode not in modes:
        raise ValueError("mode must be in {}".format(modes))


def _check_period(period):
    """check if period is acceptable"""
    if period not in [x.value for x in PERIOD]:
        raise ValueError("Period: {} not acceptable".format(period))


def _check_volume(volume):
    """normalize volume"""
    if not isinstance(volume, float):
        try:
            return float(volume)
        except Exception:
            raise ValueError("vol must be float")
    else:
        return volume


class BaseClient(object):
    """main client class"""

    def __init__(self):
        self.ws = None
        self._login_data = None
        self._time_last_request = time.time() - MAX_TIME_INTERVAL
        self.status = STATUS.NOT_LOGGED
        LOGGER.debug("BaseClient inited")
        self.LOGGER = logging.getLogger('XTBApi.api.BaseClient')

    def _send_command(self, dict_data):
        """send command to api"""
        time_interval = time.time() - self._time_last_request
        self.LOGGER.debug("took {} s.".format(time_interval))
        if time_interval < MAX_TIME_INTERVAL:
            time.sleep(MAX_TIME_INTERVAL - time_interval)
        self.ws.send(json.dumps(dict_data))
        try:
            response = self.ws.recv()
        except WebSocketConnectionClosedException:
            raise SocketError()
        self._time_last_request = time.time()
        res = json.loads(response)
        if res['status'] is False:
            raise CommandFailed(res)
        if 'returnData' in res.keys():
            self.LOGGER.info("CMD: done")
            self.LOGGER.debug(res['returnData'])
            return res['returnData']

    def _check_login(self):
        if self.status == STATUS.NOT_LOGGED:
            raise NotLogged()
        elif time.time() - self._time_last_request >= LOGIN_TIMEOUT:
            self.LOGGER.info("re-logging in due to LOGIN_TIMEOUT gone")
            self.login(self._login_data[0], self._login_data[1])

    def login(self, user_id, password):
        """login command"""
        data = _get_data("login", userId=user_id, password=password)
        self.ws = create_connection("wss://ws.xapi.pro/demo")
        response = self._send_command(data)
        self._login_data = (user_id, password)
        self.status = STATUS.LOGGED
        self.LOGGER.info("CMD: login...")
        return response

    def logout(self):
        """logout command"""
        data = _get_data("logout")
        response = self._send_command(data)
        self.status = STATUS.LOGGED
        self.LOGGER.info("CMD: logout...")
        return response

    def get_all_symbols(self):
        """getAllSymbols command"""
        self._check_login()
        data = _get_data("getAllSymbols")
        self.LOGGER.info("CMD: get all symbols...")
        return self._send_command(data)

    def get_calendar(self):
        """getCalendar command"""
        self._check_login()
        data = _get_data("getCalendar")
        self.LOGGER.info("CMD: get calendar...")
        return self._send_command(data)

    def get_chart_last_request(self, symbol, period, start):
        """getChartLastRequest command"""
        _check_period(period)
        self._check_login()
        args = {
            "period": period,
            "start": start * 1000,
            "symbol": symbol
        }
        data = _get_data("getChartLastRequest", info=args)
        self.LOGGER.info(f"CMD: get chart last request for {symbol} of period"
                         f" {period} from {start}...")

        return self._send_command(data)

    def get_chart_range_request(self, symbol, period, start, end, ticks):
        """getChartRangeRequest command"""
        _check_period(period)
        if not isinstance(ticks, int):
            raise ValueError(f"ticks value {ticks} must be int")
        self._check_login()
        args = {
            "end": end * 1000,
            "period": period,
            "start": start * 1000,
            "symbol": symbol,
            "ticks": ticks
        }
        data = _get_data("getChartRangeRequest", info=args)
        self.LOGGER.info(f"CMD: get chart range request for {symbol} of "
                         f"{period} from {start} to {end} with ticks of "
                         f"{ticks}...")
        return self._send_command(data)

    def get_commission(self, symbol, volume):
        """getCommissionDef command"""
        volume = _check_volume(volume)
        self._check_login()
        data = _get_data("getCommissionDef", symbol=symbol, volume=volume)
        self.LOGGER.info(f"CMD: get commission for {symbol} of {volume}...")
        return self._send_command(data)

    def get_margin_level(self):
        """getMarginLevel command
        get margin information"""
        self._check_login()
        data = _get_data("getMarginLevel")
        self.LOGGER.info("CMD: get margin level...")
        return self._send_command(data)

    def get_margin_trade(self, symbol, volume):
        """getMarginTrade command
        get expected margin for volumes used symbol"""
        volume = _check_volume(volume)
        self._check_login()
        data = _get_data("getMarginTrade", symbol=symbol, volume=volume)
        self.LOGGER.info(f"CMD: get margin trade for {symbol} of {volume}...")
        return self._send_command(data)

    def get_profit_calculation(self, symbol, mode, volume, op_price, cl_price):
        """getProfitCalculation command
        get profit calculation for symbol with vol, mode and op, cl prices"""
        _check_mode(mode)
        volume = _check_volume(volume)
        self._check_login()
        data = _get_data("getProfitCalculation", closePrice=cl_price,
                         cmd=mode, openPrice=op_price, symbol=symbol,
                         volume=volume)
        self.LOGGER.info(f"CMD: get profit calculation for {symbol} of"
                         f"{volume} from {op_price} to {cl_price} in mode"
                         f"{mode}...")
        return self._send_command(data)

    def get_server_time(self):
        """getServerTime command"""
        self._check_login()
        data = _get_data("getServerTime")
        self.LOGGER.info("CMD: get server time...")
        return self._send_command(data)

    def get_symbol(self, symbol):
        """getSymbol command"""
        self._check_login()
        data = _get_data("getSymbol", symbol=symbol)
        self.LOGGER.info(f"CMD: get symbol {symbol}...")
        return self._send_command(data)

    def get_tick_prices(self, symbols, start, level=0):
        """getTickPrices command"""
        self._check_login()
        data = _get_data("getTickPrices", level=level, symbols=symbols,
                         timestamp=start)
        self.LOGGER.info(f"CMD: get tick prices of {symbols} from {start} "
                         f"with level {level}...")
        return self._send_command(data)

    def get_trade_records(self, trade_position_list):
        """getTradeRecords command
        takes a list of position id"""
        self._check_login()
        data = _get_data("getTradeRecords", orders=trade_position_list)
        self.LOGGER.info(f"CMD: get trade records of len "
                         f"{len(trade_position_list)}...")
        return self._send_command(data)

    def get_trades(self, opened_only=True):
        """getTrades command"""
        self._check_login()
        data = _get_data("getTrades", openedOnly=opened_only)
        self.LOGGER.info("CMD: get trades...")
        return self._send_command(data)

    def get_trades_history(self, start, end):
        """getTradesHistory command
        can take 0 as actual time"""
        self._check_login()
        data = _get_data("getTradesHistory", end=end, start=start)
        self.LOGGER.info(f"CMD: get trades history from {start} to {end}...")
        return self._send_command(data)

    def get_trading_hours(self, trade_position_list):
        """getTradingHours command"""
        self._check_login()
        data = _get_data("getTradingHours", symbols=trade_position_list)
        self.LOGGER.info(f"CMD: get trading hours of len "
                         f"{len(trade_position_list)}...")
        return self._send_command(data)

    def get_version(self):
        """getVersion command"""
        self._check_login()
        data = _get_data("getVersion")
        self.LOGGER.info("CMD: get version...")
        return self._send_command(data)

    def ping(self):
        """ping command"""
        self._check_login()
        data = _get_data("ping")
        self.LOGGER.info("CMD: get ping...")
        return self._send_command(data)

    def trade_transaction(self, symbol, mode, trans_type, volume, **kwargs):
        """tradeTransaction command"""
        # check type
        if trans_type not in [x.value for x in TRANS_TYPES]:
            raise ValueError(f"Type must be in {[x for x in trans_type]}")
        # check kwargs
        accepted_values = ['order', 'price', 'expiration', 'customComment',
                           'offset', 'sl', 'tp']
        assert all([val in accepted_values for val in kwargs.keys()])
        _check_mode(mode)  # check if mode is acceptable
        volume = _check_volume(volume)  # check if volume is valid
        self._check_login()  # check if logged in
        info = {
            'cmd': mode,
            'symbol': symbol,
            'type': trans_type,
            'volume': volume
        }
        info.update(kwargs)  # update with kwargs parameters
        data = _get_data("tradeTransaction", tradeTransInfo=info)
        name_of_mode = [x.name for x in MODES if x.value == mode][0]
        name_of_type = [x.name for x in TRANS_TYPES if x.value ==
                        trans_type][0]
        self.LOGGER.info(f"CMD: trade transaction of {symbol} of mode "
                         f"{name_of_mode} with type {name_of_type} of "
                         f"{volume}...")
        return self._send_command(data)

    def trade_transaction_status(self, order_id):
        """tradeTransactionStatus command"""
        self._check_login()
        data = _get_data("tradeTransactionStatus", order=order_id)
        self.LOGGER.info(f"CMD: trade transaction status for {order_id}...")
        return self._send_command(data)

    def get_user_data(self):
        """getCurrentUserData command"""
        self._check_login()
        data = _get_data("getCurrentUserData")
        self.LOGGER.info("CMD: get user data...")
        return self._send_command(data)


class Transaction(object):
    def __init__(self, trans_dict):
        self._trans_dict = trans_dict
        self.order_id = trans_dict['order']
        self.symbol = trans_dict['symbol']
        self.volume = trans_dict['volume']
        self.price = trans_dict['close_price']
        self.actual_profit = trans_dict['profit']
        LOGGER.debug(f"Transaction {self.order_id} inited")


class Client(BaseClient):
    """advanced class of client"""
    def __init__(self):
        super().__init__()
        self.trade_rec = {}
        self.LOGGER = logging.getLogger('XTBApi.api.Client')
        self.LOGGER.info("Client inited")

    def update_trades(self):
        """update trade list"""
        trades = self.get_trades()
        data = trades
        for trade in data:
            obj_trans = Transaction(trade)
            self.trade_rec[obj_trans.order_id] = obj_trans
        self.LOGGER.info(f"updated {len(self.trade_rec)} trades")
        return self.trade_rec

    def get_trade_profit(self, trans_id):
        """get profit of trade"""
        self.update_trades()
        profit = self.trade_rec[trans_id].actual_profit
        self.LOGGER.info(f"got trade profit of {profit}")
        return profit

    def open_trade(self, mode, symbol, volume):
        """open trade transaction"""
        if mode in [MODES.BUY.value, MODES.SELL.value]:
            mode = [x for x in MODES if x.value == mode][0]
        elif mode in ['buy', 'sell']:
            modes = {'buy': MODES.BUY, 'sell': MODES.SELL}
            mode = modes[mode]
        else:
            raise ValueError("mode can be buy or sell")
        mode_name = mode.name
        mode = mode.value
        self.LOGGER.debug(f"opening trade of {symbol} of {volume} with "
                          f"{mode_name}")
        conversion_mode = {MODES.BUY.value: 'ask', MODES.SELL.value: 'bid'}
        price = self.get_symbol(symbol)[conversion_mode[mode]]
        response = self.trade_transaction(symbol, mode, 0, volume, price=price)
        self.update_trades()
        status = self.trade_transaction_status(response['order'])[
            'requestStatus']
        self.LOGGER.debug(f"open_trade completed with status of {status}")
        if status != 3:
            raise TransactionRejected(status)
        return response

    def _close_trade_only(self, order_id):
        """faster but less secure"""
        trade = self.trade_rec[order_id]
        self.LOGGER.debug(f"closing trade {order_id}")
        try:
            response = self.trade_transaction(
                trade.symbol, 0, 2, trade.volume, order=trade.order_id,
                price=trade.price)
        except CommandFailed as e:
            if e.err_code == 'BE51':  # order already closed
                self.LOGGER.debug("BE51 error code noticed")
                return 'BE51'
            else:
                raise
        status = self.trade_transaction_status(
            response['order'])['requestStatus']
        self.LOGGER.debug(f"close_trade completed with status of {status}")
        if status != 3:
            raise TransactionRejected(status)
        return response

    def close_trade(self, trans):
        """close trade transaction"""
        if isinstance(trans, Transaction):
            order_id = trans.order_id
        else:
            order_id = trans
        self.update_trades()
        return self._close_trade_only(order_id)

    def close_all_trades(self):
        """close all trades"""
        self.update_trades()
        self.LOGGER.debug(f"closing {len(self.trade_rec)} trades")
        trade_ids = self.trade_rec.keys()
        for trade_id in trade_ids:
            self._close_trade_only(trade_id)


# - next features -
# TODO: withdraw
# TODO: deposit
