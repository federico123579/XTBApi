#!/usr/bin/env python3
# -*- coding utf-8 -*-

from websocket import create_connection
import json

class Client(object):
    """main client class"""

    def __int__(self):
        pass

    def get_response(self):
        data = {
            "command": "login",
            "arguments": {
                "userId": "10649413",
                "password": "20072001FdRcLlL"
            }
        }
        ws = create_connection("wss://ws.xapi.pro/demo")
        ws.send(json.dumps(data))
        response = ws.recv()
        return response
