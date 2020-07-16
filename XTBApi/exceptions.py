# -*- coding utf-8 -*-

"""
XTBApi.exceptions
~~~~~~~

Exception module
"""

import logging

LOGGER = logging.getLogger('XTBApi.exceptions')


class CommandFailed(Exception):
    """When a command fail"""
    def __init__(self, response):
        self.msg = "Command failed"
        self.err_code = response['errorCode']
        self.err_desc = response['errorDescr']
        LOGGER.error(self.msg)
        LOGGER.debug(f"Error code: {self.err_code}. Error description: {self.err_desc}")
        super().__init__(self.msg)


class NotLogged(Exception):
    """When not logged"""
    def __init__(self):
        self.msg = "Not logged, please log in"
        LOGGER.exception(self.msg)
        super().__init__(self.msg)


class SocketError(Exception):
    """When socket is already closed may be the case of server internal error"""
    def __init__(self):
        self.msg = "SocketError, mey be an internal error"
        LOGGER.error(self.msg)
        super().__init__(self.msg)


class TransactionRejected(Exception):
    """Transaction rejected error"""
    def __init__(self, status_code):
        self.status_code = status_code
        self.msg = "Transaction rejected with error code {}".format(status_code)
        LOGGER.error(self.msg)
        super().__init__(self.msg)
