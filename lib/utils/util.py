#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import json
import time
import string
import random
import requests
from datetime import datetime
from lib.core.config import BaseConfig

def parser_header(headers, flag: bool = True):
    """解析headers并返回"""

    res_headers = {}
    for key, value in headers.items():
        res_headers[key] = value
    if flag:
        if 'Content-Length' in res_headers.keys():
            res_headers.pop("Content-Length")

    return res_headers

def get_time(timestamp=None):
    if timestamp:
        return datetime.fromtimestamp(timestamp)
    else:
        return datetime.fromtimestamp(time.time())

def get_timestamp():
    return time.time()

def random_string(length=32):
    return ''.join([random.choice(
        string.ascii_letters + string.digits + '_'
    ) for _ in range(length)])


def get_safe_ex_string(ex):
    """异常消息处理"""

    if getattr(ex, "message", None):
        retVal = ex.message
    elif getattr(ex, "msg", None):
        retVal = ex.msg
    else:
        retVal = str(ex)
    return retVal

def seng_message(msg="", reminders=None):

    if reminders is None:
        reminders = []

    url = BaseConfig.DINGDING_ROBOT_URL
    timeout = BaseConfig.TIMEOUT
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "msgtype": "text",
        "at": {
            "atMobiles": reminders,
            "isAtAll": False,
        },
        "text": {
            "content": msg,
        }
    }
    error = ""
    for i in range(0, 3):
        try:
            r = requests.post(url, data=json.dumps(data), headers=headers, timeout=timeout)
            return True, r.text
        except Exception as e:
            error = get_safe_ex_string(e)
    return False, error

