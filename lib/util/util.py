#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import time
import string
import random
from datetime import timedelta
from datetime import datetime

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

def get_timedelta(seconds=3600):
    return timedelta(seconds=seconds)

def get_time_str(date: datetime = None, fmt="%Y-%m-%d %H:%M:%S") -> str:
    """获取时间字符串"""

    if date:
        return datetime.strftime(date, fmt)
    else:
        return datetime.strftime(get_time(), fmt)


def get_safe_ex_string(ex):
    """异常消息处理"""

    if getattr(ex, "message", None):
        retVal = ex.message
    elif getattr(ex, "msg", None):
        retVal = ex.msg
    else:
        retVal = str(ex)
    return retVal
