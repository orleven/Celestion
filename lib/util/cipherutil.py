#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from jwt import PyJWT
from base64 import b64encode
from base64 import b64decode
from urllib.parse import unquote
from urllib.parse import quote

def jwtencode(message, secret_key, algorithm='HS256'):
    """jwt 加密"""
    instance = PyJWT()
    data = instance.encode(message, secret_key, algorithm=algorithm)
    return data

def jwtdecode(token, secret_key, algorithms=None, do_time_check=True):
    """jwt 解密"""
    if algorithms is None:
        algorithms = ["HS256"]

    instance = PyJWT()
    data = instance.decode(token, secret_key, algorithms=algorithms, do_time_check=do_time_check)
    return data



def urldecode(value, encoding='utf-8'):
    """url解码"""

    return unquote(value, encoding)


def safe_urldecode(value, encoding='utf-8'):
    """url解码, 不报错版"""

    try:
        return urldecode(value, encoding)
    except:
        return None


def urlencode(value, encoding='utf-8'):
    """url编码"""

    return quote(value, encoding)

def safe_urlencode(value, encoding='utf-8'):
    """url编码, 不报错版"""
    try:
        return urlencode(value, encoding)
    except:
        return None


def base64encode(value, table=None, encoding='utf-8'):
    """base64编码"""
    b64_table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    if type(value) is not bytes:
        value = bytes(value, encoding)
    if table:
        return str(str.translate(str(b64encode(value)), str.maketrans(b64_table, table)))[2:-1]
    else:
        return str(b64encode(value), encoding=encoding)


def safe_base64encode(value, table=None, encoding='utf-8'):
    """base64编码, 不报错版"""
    try:
        return base64encode(value, table, encoding)
    except:
        return None


def base64decode(value, table=None, encoding='utf-8'):
    """base64解码"""
    b64_table = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    if table:
        return b64decode(str.translate(value, str.maketrans(table, b64_table)))
    else:
        if type(value) is not bytes:
            value = bytes(value, encoding)
        return b64decode(value)


def safe_base64decode(value, table=None, encoding='utf-8'):
    """base64解码, 不报错版"""
    try:
        result = base64decode(value, table, encoding)
        if isinstance(result, bytes):
            result = result.decode(encoding)
        return result
    except:
        return None