#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from lib.core.config import Config
from lib.core.config import BaseConfig
from lib.core.config import DataBaseConfig

app = Flask('celestion', template_folder=Config.TEMPLATES_PATH, static_folder=Config.STATICS_PATH, static_url_path='/' + Config.STATICS)
app.config.from_object(DataBaseConfig)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = BaseConfig.SEND_FILE_MAX_AGE_DEFAULT
app.config['SECRET_KEY'] = BaseConfig.SECRET_KEY
app.config["DEBUG"] = False
db = SQLAlchemy(app)

from lib.handers import basehander
app.register_blueprint(basehander.mod)

from lib.handers import indexhander
app.register_blueprint(indexhander.mod)

from lib.handers import apihander
app.register_blueprint(apihander.mod)

from lib.handers.manager.log import webloghander
app.register_blueprint(webloghander.mod)

from lib.handers.manager.log import dnsloghander
app.register_blueprint(dnsloghander.mod)

from lib.handers.manager.setting import responsehander
app.register_blueprint(responsehander.mod)

from lib.handers.manager.setting import dnshander
app.register_blueprint(dnshander.mod)

from lib.handers.manager.system import userhander
app.register_blueprint(userhander.mod)

from lib.handers.manager.system import loghander
app.register_blueprint(loghander.mod)
