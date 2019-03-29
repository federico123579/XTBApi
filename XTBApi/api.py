# -*- coding utf-8 -*-

"""
XTBApi.api
~~~~~~~

Main module
"""

import json

from websocket import create_connection


def _get_data(command, **parameters):
    data = {
        "command": command,
    }
    if len(parameters) > 0:
        data['arguments'] = {}
        for key, value in parameters.items():
            data['arguments'][key] = value
    return data


def _get_streaming_data(command, **parameters):
    data = {
        "command": command,
    }
    for key, value in parameters.items():
        data[key] = value
    return data


class Client(object):
    """main client class"""

    def __init__(self):
        self.ws = create_connection("wss://ws.xapi.pro/demo")
        self.stream_ws = create_connection("wss://ws.xapi.pro/demoStream")
        self._stream_id = None

    def _send_command(self, dict_data):
        """send command to api"""
        self.ws.send(json.dumps(dict_data))
        response = self.ws.recv()
        return json.loads(response)

    def _send_streaming_command(self, dict_data):
        """send streaming command to api"""
        dict_data['streamSessionId'] = self._stream_id
        self.stream_ws.send(json.dumps(dict_data))
        response = self.stream_ws.recv()
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

    def get_balance(self):
        """getBalance streaming command"""
        data = _get_streaming_data("getBalance")
        return self._send_streaming_command(data)

    def get_candles(self, symbol):
        """getCandles streaming command"""
        data = _get_streaming_data("getCandles", symbol=symbol)
        return self._send_streaming_command(data)

    def get_all_symbols(self):
        """getAllSymbols command"""
        data = _get_data("getAllSymbols")
        return self._send_command(data)

    def get_calendar(self):
        """getCalendar command"""
        data = _get_data("getCalendar")
        return self._send_command(data)

    def get_commission(self, symbol, vol):
        """getCommissionDef command"""
        data = _get_data("getCommissionDef", symbol=symbol, volume=vol)
        return self._send_command(data)

    def get_user_data(self):
        """getCurrentUserData command"""
        data = _get_data("getCurrentUserData")
        return self._send_command(data)