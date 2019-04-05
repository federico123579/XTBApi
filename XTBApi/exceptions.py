# -*- coding utf-8 -*-

"""
XTBApi.exceptions
~~~~~~~

Exception module
"""

import logging

LOGGER = logging.getLogger('XTBApi.exceptions')


class CommandFailed(Exception):
    """when a command fail"""
    def __init__(self, response):
        self.msg = "command failed"
        LOGGER.exception(response)
        super().__init__(self.msg)


class NotLogged(Exception):
    """when not logged"""
    def __init__(self):
        self.msg = "Not logged, please log in"
        super().__init__(self.msg)
