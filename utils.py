import sys
import time
import datetime
import requests


def printErrorEndl(error):
    sys.stderr.write(f"[{datetime.datetime.now()}] Error: {error}\n")
    sys.stderr.flush()


def myPost(url, cookies, data, headers=None):
    while True:
        try:
            response = requests.post(
                url, headers=headers, cookies=cookies, data=data)
            if response.status_code == 200:
                return response
            printErrorEndl(response.status_code)
            time.sleep(5)
        except Exception as e:
            printErrorEndl(e)
            time.sleep(10)


def myGet(url, cookies, headers=None):
    while True:
        try:
            response = requests.get(url, headers=headers, cookies=cookies)
            if response.status_code == 200:
                return response
            printErrorEndl(response.status_code)
            time.sleep(5)
        except Exception as e:
            printErrorEndl(e)
            time.sleep(10)
