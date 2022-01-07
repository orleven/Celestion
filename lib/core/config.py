#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import os

class Config(object):
    """
    配置
    """
    # 当前版本
    VERSION = "1.0"

    # 版本标志
    VERSION_STRING = f"celestion/{VERSION}"

    # 描述
    DESCRIPTION = 'Celestion is a non-echoed vulnerability testing auxiliary platform. The platform is written in flask and provides DNSLOG, HTTPLOG and other functions. (in dev).'

    # 目录配置
    STATICS = 'static'
    ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    STATICS_PATH = os.path.join(ROOT_PATH, STATICS)
    LOGS_PATH = os.path.join(ROOT_PATH, 'logs')
    TEMPLATES_PATH = os.path.join(ROOT_PATH, 'templates')


class BaseConfig(object):
    """
    基础配置
    """
    # MD5的盐
    HALT = 'BBXiU0HLdxlH1eBp8lQur2RlWEwfIwoO'

    # SECRET KEY
    SECRET_KEY = '#ma=s-l!2obwj%h-6uu^sbw+4%i2w79%v3^ill62k3&7tjf5dc'

    # SEND FILE MAX AGE DEFAULT
    SEND_FILE_MAX_AGE_DEFAULT = 0

    # A.com的域名的NS记录
    NS1_DOMAIN = 'ns1.A.com'
    NS2_DOMAIN = 'ns2.A.com'

    # B.com，主要做DNS记录
    DNS_DOMAIN = 'B.com'

    # B.com 的默认解析地址
    DEFAULT_SERVER_IP = '127.0.0.1'

    # 记录管理的域名
    ADMIN_DOMAIN = 'admin.B.com'

    # admin域名解析地址
    ADMIN_SERVER_IP = '127.0.0.1'

    # 控制台默认密码
    DEFAUTL_PASSWORD = 'Celestion@123'

    # 钉钉机器人api地址
    DINGDING_ROBOT_URL = 'https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxx'

    # 超时
    TIMEOUT = 5

class DataBaseConfig(object):
    """
    数据库配置
    """

    MYSQL_USERNAME = 'root'
    MYSQL_PASSWORD = '123456'
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_DBNAME = 'celestion'
    MYSQL_CHARSET = 'utf8mb4'
    MYSQL_COLLATE = 'utf8mb4_general_ci'
    MYSQL_SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DBNAME}?charset={MYSQL_CHARSET}'

    SQLITE_DBNAME = 'celestion'
    SQLTIE_SQLALCHEMY_DATABASE_URI = f'sqlite+pysqlite:///{Config.ROOT_PATH}/{SQLITE_DBNAME}.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_ECHO = False

    # 数据库类型，默认为SQLite，如需要使用mysql，切换即可
    # SQLALCHEMY_DATABASE_URI = MYSQL_SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_DATABASE_URI = SQLTIE_SQLALCHEMY_DATABASE_URI

    if SQLALCHEMY_DATABASE_URI.startswith("mysql"):
        SQLALCHEMY_POOL_SIZE = 100
        SQLALCHEMY_MAX_OVERFLOW = 20
