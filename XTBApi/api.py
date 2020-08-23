# -*- coding utf-8 -*-

"""
XTBApi.api
~~~~~~~

Main module
"""

import json
import time
from datetime import datetime
from websocket import create_connection, WebSocketConnectionClosedException
from XTBApi.exceptions import *

LOGGER = logging.getLogger('XTBApi.api')
STATUS = {'LOGGED': 1, 'NOT_LOGGED': 2}
MODES = {'BUY': 0, 'SELL': 1, 'BUY_LIMIT': 2, 'SELL_LIMIT': 3, 'BUY_STOP': 4, 'SELL_STOP': 5, 'BALANCE': 6, 'CREDIT': 7}
TRANS_TYPES = {'OPEN': 0, 'PENDING': 1, 'CLOSE': 2, 'MODIFY': 3, 'DELETE': 4}
PERIOD = {'1M': 1, '5M': 5, '15M': 15, '30M': 30, '1H': 60, '4H': 240, '1D': 1440, '1W': 10080, '1MN': 43200}
MAX_TIME_INTERVAL = 0.200


def check_mode(mode):
    """Check if mode is acceptable"""
    modes = [MODES[x] for x in MODES]
    if mode not in modes:
        raise ValueError("mode must be in {}".format(modes))


def check_period(period):
    """Check if period is acceptable"""
    if period not in PERIOD.values():
        raise ValueError("Period: {} not acceptable".format(period))


def check_volume(volume):
    """Normalize volume"""
    if not isinstance(volume, float):
        try:
            return float(volume)
        except Exception:
            raise ValueError("Volume must be float")
    else:
        return volume


def get_data(command, **parameters):
    """Creates a dictionary for a given command and parameters"""
    data = {"command": command}
    if parameters:
        data['arguments'] = {}
        for (key, value) in parameters.items():
            data['arguments'][key] = value
    return data


class BaseClient(object):
    """Base Client class"""

    def __init__(self):
        self.ws = None
        self._login_data = None
        self.session_id = None
        self._time_last_request = time.time()
        self.status = STATUS['NOT_LOGGED']
        self.max_time = MAX_TIME_INTERVAL
        LOGGER.debug("BaseClient inited")

    def login_decorator(self, func, *args, **kwargs):
        """Check if login was successful and tries to login if it failed before"""
        if self.status == STATUS['NOT_LOGGED']:
            raise NotLogged()
        try:
            return func(*args, **kwargs)
        except SocketError:
            LOGGER.info("Re-logging in due to login timeout gone")
            self.login(self._login_data[0], self._login_data[1])
            return func(*args, **kwargs)
        except Exception as e:
            raise e

    def send_command(self, dict_data):
        """Send a command to the API"""
        time_interval = time.time() - self._time_last_request
        LOGGER.debug("Last request: {} seconds ago".format(time_interval))
        if time_interval < self.max_time:
            time.sleep(self.max_time - time_interval)
        try:
            self.ws.send(json.dumps(dict_data))
            response = self.ws.recv()
        except WebSocketConnectionClosedException:
            raise SocketError()
        self._time_last_request = time.time()
        res = json.loads(response)
        if res['status'] is False:
            raise CommandFailed(res)
        LOGGER.info("Command successful: {}".format(dict_data['command']))
        if 'returnData' in res.keys():
            LOGGER.debug(res['returnData'])
            return res['returnData']
        return res

    def send_command_with_check(self, dict_data):
        """Send a command to the API with login check"""
        return self.login_decorator(self.send_command, dict_data)

    def login(self, user_id, password, mode='demo'):
        """login command"""
        LOGGER.info('Sending command: login')
        data = get_data("login", userId=user_id, password=password)
        self.ws = create_connection(f"wss://ws.xtb.com/{mode}")
        response = self.send_command(data)
        self._login_data = (user_id, password)
        self.status = STATUS['LOGGED']
        self.session_id = response['streamSessionId']
        return response

    def logout(self):
        """logout command"""
        LOGGER.info('Sending command: logout')
        data = get_data("logout")
        response = self.send_command(data)
        self.status = STATUS['LOGGED']
        return response

    def get_all_symbols(self):
        """getAllSymbols command"""
        LOGGER.info('Sending command: getAllSymbols')
        data = get_data("getAllSymbols")
        return self.send_command_with_check(data)

    def get_calendar(self):
        """getCalendar command"""
        LOGGER.info('Sending command: getCalendar')
        data = get_data("getCalendar")
        return self.send_command_with_check(data)

    def get_chart_last_request(self, symbol, period, start):
        """getChartLastRequest command"""
        LOGGER.info(f"Sending command: getChartLastRequest (Symbol: {symbol}, Period: {period}, Start: {start})")
        check_period(period)
        args = {"period": period, "start": start * 1000, "symbol": symbol}
        data = get_data("getChartLastRequest", info=args)
        return self.send_command_with_check(data)

    def get_chart_range_request(self, symbol, period, start, end, ticks):
        """getChartRangeRequest command"""
        LOGGER.info(f"Sending command: getChartRangeRequest (Symbol: {symbol}, Period: {period}, Start: {start}, "
                    f"End: {end}, Ticks: {ticks})")
        if not isinstance(ticks, int):
            raise ValueError(f"Ticks value {ticks} must be int")
        args = {"end": end * 1000, "period": PERIOD[period], "start": start * 1000, "symbol": symbol, "ticks": ticks}
        data = get_data("getChartRangeRequest", info=args)
        return self.send_command_with_check(data)

    def get_commission(self, symbol, volume):
        """getCommissionDef command"""
        LOGGER.info(f"Sending command: getComissionDef (Symbol: {symbol}, Volume: {volume})")
        volume = check_volume(volume)
        data = get_data("getCommissionDef", symbol=symbol, volume=volume)
        return self.send_command_with_check(data)

    def get_margin_level(self):
        """getMarginLevel command"""
        LOGGER.info('Sending command: getMarginLevel')
        data = get_data("getMarginLevel")
        return self.send_command_with_check(data)

    def get_margin_trade(self, symbol, volume):
        """getMarginTrade command"""
        LOGGER.info(f"Sending command: getMarginTrade (Symbol: {symbol}, Volume: {volume})")
        volume = check_volume(volume)
        data = get_data("getMarginTrade", symbol=symbol, volume=volume)
        return self.send_command_with_check(data)

    def get_profit_calculation(self, symbol, mode, volume, op_price, cl_price):
        """getProfitCalculation command"""
        LOGGER.info(f"Sending command: getProfitCalculation (Symbol: {symbol}, Volume: {volume}, " 
                    f"Open Price: {op_price}, Close Price: {cl_price}, Mode: {mode})")
        check_mode(mode)
        volume = check_volume(volume)
        data = get_data("getProfitCalculation", closePrice=cl_price, cmd=mode, openPrice=op_price, symbol=symbol,
                        volume=volume)
        return self.send_command_with_check(data)

    def get_server_time(self):
        """getServerTime command"""
        LOGGER.info("Sending command: getServerTime")
        data = get_data("getServerTime")
        return self.send_command_with_check(data)

    def get_symbol(self, symbol):
        """getSymbol command"""
        LOGGER.info(f"Sending command: getSymbol (Symbol: {symbol})")
        data = get_data("getSymbol", symbol=symbol)
        return self.send_command_with_check(data)

    def get_tick_prices(self, symbols, start, level=0):
        """getTickPrices command"""
        LOGGER.info(f"Sending command: getTickPrices (Symbols: {symbols}, Start: {start}, Level {level})")
        data = get_data("getTickPrices", level=level, symbols=symbols, timestamp=start)
        return self.send_command_with_check(data)

    def get_trade_records(self, trade_position_list):
        """getTradeRecords command"""
        LOGGER.info(f"Sending command: getTradeRecords (Orders: {trade_position_list})")
        data = get_data("getTradeRecords", orders=trade_position_list)
        return self.send_command_with_check(data)

    def get_trades(self, opened_only=True):
        """getTrades command"""
        LOGGER.info(f"Sending command: getTrades (Opened Only: {opened_only})")
        data = get_data("getTrades", openedOnly=opened_only)
        return self.send_command_with_check(data)

    def get_trades_history(self, start, end):
        """getTradesHistory command"""
        LOGGER.info(f"Sending command: get_trades_history (Start: {start}, End: {end})")
        data = get_data("getTradesHistory", end=end, start=start)
        return self.send_command_with_check(data)

    def get_trading_hours(self, symbols):
        """getTradingHours command"""
        LOGGER.info(f"Sending command: getTradingHours (Symbols: {symbols})")
        data = get_data("getTradingHours", symbols=symbols)
        response = self.send_command_with_check(data)
        for symbol in response:
            for day in symbol['trading']:
                day['fromT'] = int(day['fromT'] / 1000)
                day['toT'] = int(day['toT'] / 1000)
            for day in symbol['quotes']:
                day['fromT'] = int(day['fromT'] / 1000)
                day['toT'] = int(day['toT'] / 1000)
        return response

    def get_version(self):
        """getVersion command"""
        LOGGER.info("Sending command: getVersion")
        data = get_data("getVersion")
        return self.send_command_with_check(data)

    def ping(self):
        """ping command"""
        LOGGER.info("Sending command: ping")
        data = get_data("ping", streamSessionId=self.session_id)
        self.send_command_with_check(data)

    def trade_transaction(self, symbol, mode, trans_type, volume, **kwargs):
        """tradeTransaction command"""
        if trans_type not in TRANS_TYPES.values():
            raise ValueError(f"Type must be in {[x for x in TRANS_TYPES.values()]}")  # Check type

        name_of_mode = [x for x in MODES if MODES[x] == mode][0]
        name_of_type = [x for x in TRANS_TYPES if TRANS_TYPES[x] == trans_type][0]
        LOGGER.info(f"Sending command: tradeTransaction (Symbol: {symbol}, Mode: {name_of_mode}, "
                    f"Type: {name_of_type}, Volume: {volume})")

        accepted_values = ['order', 'price', 'expiration', 'customComment', 'offset', 'sl', 'tp']  # Check kwargs
        assert all([val in accepted_values for val in kwargs.keys()])
        check_mode(mode)  # Check mode
        volume = check_volume(volume)  # Check volume
        info = {'cmd': mode, 'symbol': symbol, 'type': trans_type, 'volume': volume}
        info.update(kwargs)  # Update with kwargs parameters
        data = get_data("tradeTransaction", tradeTransInfo=info)
        return self.send_command_with_check(data)

    def trade_transaction_status(self, order_id):
        """tradeTransactionStatus command"""
        LOGGER.info(f"Sending command: tradeTransactionStatus (Order: {order_id})")
        data = get_data("tradeTransactionStatus", order=order_id)
        return self.send_command_with_check(data)

    def get_user_data(self):
        """getCurrentUserData command"""
        LOGGER.info("Sending command: getCurrentUserData")
        data = get_data("getCurrentUserData")
        return self.send_command_with_check(data)


class Transaction(object):
    def __init__(self, trans_dict):
        self._trans_dict = trans_dict
        self.mode = trans_dict['cmd']
        self.order_id = trans_dict['order']
        self.symbol = trans_dict['symbol']
        self.volume = trans_dict['volume']
        self.price = trans_dict['close_price']
        self.actual_profit = trans_dict['profit']
        self.timestamp = trans_dict['open_time'] / 1000
        LOGGER.debug(f"Transaction {self.order_id} updated")


class Client(BaseClient):
    """Advanced class of client"""
    def __init__(self):
        super().__init__()
        self.trade_rec = {}
        LOGGER.info("Client inited")

    def check_if_market_open(self, list_of_symbols):
        """check if market is open for symbol in symbols"""
        now = datetime.today()
        actual_time = now.hour * 3600 + now.minute * 60 + now.second
        response = self.get_trading_hours(list_of_symbols)
        market_values = {}
        for symbol in response:
            today_values = [day for day in symbol['trading'] if day['day'] == now.isoweekday()][0]
            if today_values['fromT'] <= actual_time <= today_values['toT']:
                market_values[symbol['symbol']] = True
            else:
                market_values[symbol['symbol']] = False
        return market_values

    def get_candles(self, symbol, period, number):
        """Get last n candles of given period"""
        tmf = PERIOD[period] * 60
        sec_prior = tmf * number
        LOGGER.info(f"Get Candles (Symbol: {symbol}, Timeframe: {tmf}, Time Difference: {time.time() - sec_prior})")
        res = {'rateInfos': []}
        while len(res['rateInfos']) < number:
            res = self.get_chart_last_request(symbol, tmf // 60, time.time() - sec_prior)
            res['rateInfos'] = res['rateInfos'][-number:]
            sec_prior *= 3  # TODO: Improve this method in order to send less requests to the API
        candle_history = []
        for candle in res['rateInfos']:
            pr = candle['open']
            op_pr = pr / 10 ** res['digits']
            cl_pr = (pr + candle['close']) / 10 ** res['digits']
            hg_pr = (pr + candle['high']) / 10 ** res['digits']
            lw_pr = (pr + candle['low']) / 10 ** res['digits']
            new_candle_entry = {'ctm': candle['ctm'] / 1000, 'ctmString': candle['ctmString'], 'open': op_pr,
                                'close': cl_pr, 'high': hg_pr, 'low': lw_pr, 'volume': candle['vol']}
            candle_history.append(new_candle_entry)
        LOGGER.debug(candle_history)
        return candle_history

    def update_trades(self):
        """Update trade list"""
        trades = self.get_trades()
        self.trade_rec.clear()
        for trade in trades:
            obj_trans = Transaction(trade)
            self.trade_rec[obj_trans.order_id] = obj_trans
        LOGGER.info(f"Updated {len(self.trade_rec)} trades")
        return self.trade_rec

    def get_trade_profit(self, trans_id):
        """Get profit of trade"""
        self.update_trades()
        profit = self.trade_rec[trans_id].actual_profit
        LOGGER.info(f"Got trade profit of {profit}")
        return profit

    def open_trade(self, mode, symbol, volume, margin=None, sl=None, tp=None):
        """Open trade transaction (buy/sell) only"""
        if mode in ['buy', 'sell']:
            mode = MODES[mode.upper()]
        elif mode in ['BUY', 'SELL']:
            mode = MODES[mode]
        elif mode in [0, 1]:
            pass
        else:
            raise ValueError("Mode can only be buy or sell")
        symbol_info = self.get_symbol(symbol)
        price = {0: symbol_info['ask'], 1: symbol_info['bid']}
        leverage = symbol_info['leverage'] / 100
        if margin:
            volume = round(margin / (symbol_info['contractSize'] * leverage), 2)
        if volume < symbol_info['lotMin'] or volume > symbol_info['lotMax']:
            raise ValueError(f"Volume must be between {symbol_info['lotMin']} and {symbol_info['lotMax']}")
        if sl:
            sl = round(price[mode] * (1 - (-1) ** mode * sl * leverage), symbol_info['precision'])
        if tp:
            tp = round(price[mode] * (1 + (-1) ** mode * tp * leverage), symbol_info['precision'])
        LOGGER.info(f"Opening trade of {symbol} (Volume: {volume}, Mode: {mode})")
        response = self.trade_transaction(symbol, mode, 0, volume, price=price[mode], sl=sl, tp=tp)
        self.update_trades()
        status = self.trade_transaction_status(response['order'])['requestStatus']
        LOGGER.info(f"Trade {response['order']} opened with status of {status}")
        if status != 3:
            raise TransactionRejected(status)
        return response

    def close_trade_only(self, order_id):
        """Close trade without updating transactions"""
        trade = self.trade_rec[order_id]
        LOGGER.info(f"Closing trade {order_id}")
        try:
            response = self.trade_transaction(trade.symbol, 0, 2, trade.volume, order=trade.order_id, price=trade.price)
        except CommandFailed as e:
            raise CommandFailed(e)
        status = self.trade_transaction_status(response['order'])['requestStatus']
        LOGGER.info(f"Close trade completed with status {status}")
        if status != 3:
            raise TransactionRejected(status)
        return response

    def close_trade(self, trans):
        """Close trade transaction"""
        if isinstance(trans, Transaction):
            order_id = trans.order_id
        else:
            order_id = trans
        self.update_trades()
        return self.close_trade_only(order_id)

    def close_all_trades(self):
        """Close all trades"""
        self.update_trades()
        LOGGER.info(f"Closing {len(self.trade_rec)} trades")
        trade_ids = self.trade_rec.keys()
        for trade_id in trade_ids:
            self.close_trade_only(trade_id)
