#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from lib.core.env import *
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from lib.core.g import conf
from lib.core.g import mysql

app = Flask(PROJECT_NAME, template_folder=TEMPLATE_PATH, static_folder=STATIC_PATH, static_url_path=f"{PREFIX_URL}/{STATIC}")
app.config['SQLALCHEMY_DATABASE_URI'] = mysql.get_sqlalchemy_database_url()
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 100
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config["DEBUG"] = False
app.config['SECRET_KEY'] = conf.basic.secret_key
db = SQLAlchemy(app)

from lib.hander import basehander
app.register_blueprint(basehander.mod)

from lib.hander import indexhander
app.register_blueprint(indexhander.mod)

from lib.hander import apihander
app.register_blueprint(apihander.mod)

from lib.hander.manager.log import webloghander
app.register_blueprint(webloghander.mod)

from lib.hander.manager.log import dnsloghander
app.register_blueprint(dnsloghander.mod)

from lib.hander.manager.setting import responsehander
app.register_blueprint(responsehander.mod)

from lib.hander.manager.setting import dnshander
app.register_blueprint(dnshander.mod)

from lib.hander.manager.system import userhander
app.register_blueprint(userhander.mod)

from lib.hander.manager.system import loghander
app.register_blueprint(loghander.mod)
