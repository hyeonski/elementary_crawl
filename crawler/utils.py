import sys
import time
import datetime
import requests


def print_error_endl(error):
    sys.stderr.write(f"[{datetime.datetime.now()}] Error: {error}\n")
    sys.stderr.flush()


def my_post(url, cookies, data, headers=None):
    while True:
        try:
            response = requests.post(
                url, headers=headers, cookies=cookies, data=data)
            if response.status_code == 200:
                return response
            print_error_endl(response.status_code)
            time.sleep(5)
        except Exception as e:
            print_error_endl(e)
            time.sleep(10)


def my_get(url, cookies, headers=None):
    while True:
        try:
            response = requests.get(url, headers=headers, cookies=cookies)
            if response.status_code == 200:
                return response
            print_error_endl(response.status_code)
            time.sleep(5)
        except Exception as e:
            print_error_endl(e)
            time.sleep(10)
