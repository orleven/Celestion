#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

class LOG_STATUS:
    """
    日志状态
    """
    OK = 'OK'
    DELETE = 'Delete'

class USER_STATUS:
    """
    用户状态
    """
    OK = 'OK'
    BAN = 'Ban'

class ROLE:
    ADMIN = 'Admin'
    USER = 'User'
    GUEST = 'Guest'

class CUSTOM_LOGGING:
    SUCCESS = 9
    ERROR = 8
    WARNING = 7
    INFO = 6
    DEBUG = 5
    CRITICAL = 10


class LOG_TYPE:
    LOGIN = 'Login'
    API = 'API'
    SSO = 'SSO'
    OTHER = 'Other'

class DNS_REDIRECE:
    TRUE = True
    FALSE = False

class API_STATUS:
    """后端API接口返回码"""
    INIT = {'status': 0, 'msg': '', 'data': {'res': []}}
    SUCCESS = {'status': 10000, 'msg': 'Success!', 'data': {'res': []}}
    ERROR = {'status': 20000, 'msg': 'System error!', 'data': {'res': []}}
    ERROR_INVALID_INPUT = {'status': 20001, 'msg': 'Invalid input!', 'data': {'res': []}}
    ERROR_INVALID_INPUT_ADDON_NAME = {'status': 20001, 'msg': 'Invalid addon name!', 'data': {'res': []}}
    ERROR_INVALID_INPUT_EMAIL = {'status': 20001, 'msg': 'Invalid email!', 'data': {'res': []}}
    ERROR_INVALID_INPUT_USERNAME = {'status': 20001, 'msg': 'Invalid username!', 'data': {'res': []}}
    ERROR_INVALID_INPUT_FILE = {'status': 20001, 'msg': 'Invalid file!', 'data': {'res': []}}
    ERROR_INVALID_INPUT_PASSWORD = {'status': 20001, 'msg': 'Invalid password!', 'data': {'res': []}}
    ERROR_INVALID_INPUT_MOBILE = {'status': 20001, 'msg': 'Invalid mobile!', 'data': {'res': []}}
    ERROR_INVALID_TOKEN = {'status': 20002, 'msg': 'Invalid token!', 'data': {'res': []}}

    ERROR_IS_NOT_EXIST = {'status': 30001, 'msg': 'Data is not exist!', 'data': {'res': []}}
    ERROR_PRIMARY = {'status': 30002, 'msg': 'Data existed!', 'data': {'res': []}}
    ERROR_LOGIN = {'status': 30003, 'msg': 'Incorrect username or password!', 'data': {'res': []}}  # 登陆失败
    ERROR_ACCOUNT = {'status': 30004, 'msg': 'Abnormal account!', 'data': {'res': []}}  # 账户异常
    ERROR_INVALID_API_KEY = {'status': 30005, 'msg': 'Invalid api-key!', 'data': {'res': []}}
    ERROR_ACCESS = {'status': 30006, 'msg': 'Invalid access!', 'data': {'res': []}}  # 非法访问

    ERROR_400 = {'status': 40000, 'msg': 'Bad Request!', 'data': {'res': []}}
    ERROR_ILLEGAL_PROTOCOL = {'status': 40001, 'msg': 'Illegal protocol!', 'data': {'res': []}}  # 解析失败
    ERROR_MISSING_PARAMETER = {'status': 40002, 'msg': 'Missing parameter!', 'data': {'res': []}}  # 缺乏参数
    ERROR_404 = {'status': 40004, 'msg': 'Not Found!', 'data': {'res': []}}
    ERROR_500 = {'status': 40005, 'msg': '500 Error!', 'data': {'res': []}}

    UNKNOWN = {'status': 99999, 'msg': 'Unknown error! Please contact the administrator!', 'data': {'res': []}}

