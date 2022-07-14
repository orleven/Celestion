#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from lib.util.cipherutil import urlencode


class Mysql(object):

    def __init__(self, host="127.0.0.1", port=6379, username=None, password=None, dbname=None, charset="utf8mb4",
                 collate="utf8mb4_general_ci"):
        self.host = host
        self.port = port
        self.username = username
        if isinstance(password, int):
            password = str(password)
        self.password = urlencode(password)
        self.dbname = dbname
        self.charset = charset
        self.collate = collate
        self.sync_sqlalchemy_database_url = f'mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}?charset={self.charset}'
        self.sync_sqlalchemy_database_url_without_db = f'mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/'

    def get_sqlalchemy_database_url(self):
        """Sync 使用"""
        return self.sync_sqlalchemy_database_url

    def get_sqlalchemy_database_url_without_db(self):
        """Async 使用"""
        return self.sync_sqlalchemy_database_url_without_db
