"""
tests.test_api.py
~~~~~~~

test the api client
"""

from XTBApi.api import Client


def test_login():
    client = Client()
    response = client.get_response()
    print(response)
