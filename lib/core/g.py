#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from lib.core.config import config_parser
from lib.core.log import Logger
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from lib.core.mysql import Mysql

conf = config_parser()

cache_log = Logger(name='cache', use_console=False)

server_log = Logger(name='server', use_console=True)

access_log = Logger(name='access', use_console=False)

log = server_log

mysql = Mysql(
    host=conf.mysql.host,
    port=conf.mysql.port,
    username=conf.mysql.username,
    password=conf.mysql.password,
    dbname=conf.mysql.dbname,
    charset=conf.mysql.charset,
    collate=conf.mysql.collate,
)

sqlalchemy_database_url = mysql.get_sqlalchemy_database_url()
engine = create_engine(sqlalchemy_database_url)
engine_session = sessionmaker(engine)
