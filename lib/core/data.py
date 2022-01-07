#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import os
import sys
from queue import Queue
from lib.core.config import DataBaseConfig
from lib.core.log import Logger
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

main_name = os.path.split(os.path.splitext(sys.argv[0])[0])[-1]

cache_log = Logger(name='cache', use_console=False)

server_log = Logger(name='server', use_console=True)

access_log = Logger(name='access', use_console=False)

log = server_log

engine = create_engine(DataBaseConfig.SQLALCHEMY_DATABASE_URI)

engine_session = sessionmaker(engine)

msg_queue = Queue()



