from sys import stderr
from time import sleep
from datetime import datetime
import requests


def print_error_endl(error):
    stderr.write(f"[{datetime.now()}] Error: {error}\n")
    stderr.flush()


def my_post(url, cookies, data, headers=None):
    while True:
        try:
            response = requests.post(
                url, headers=headers, cookies=cookies, data=data)
            if response.status_code == 200:
                return response
            print_error_endl(response.status_code)
            sleep(5)
        except Exception as e:
            print_error_endl(e)
            sleep(10)


def my_get(url, cookies, headers=None):
    while True:
        try:
            response = requests.get(url, headers=headers, cookies=cookies)
            if response.status_code == 200:
                return response
            print_error_endl(response.status_code)
            sleep(5)
        except Exception as e:
            print_error_endl(e)
            sleep(10)
