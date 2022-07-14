#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import os
import sys
import socket
from datetime import timedelta

# 不生成pyc
sys.dont_write_bytecode = True

# 最低python运行版本
REQUIRE_PY_VERSION = (3, 9)

# 检测当前运行版本
RUN_PY_VERSION = sys.version_info
if RUN_PY_VERSION < REQUIRE_PY_VERSION:
    exit(f"[-] Incompatible Python version detected ('{RUN_PY_VERSION}). For successfully running program you'll have to use version {REQUIRE_PY_VERSION}  (visit 'http://www.python.org/download/')")

# 项目名称
PROJECT_NAME = "Celestion"

# 当前扫描器版本
VERSION = "1.0"

# 版本描述
# VERSION_STRING = f"{PROJECT_NAME}/{VERSION}"
VERSION_STRING = "X"

# 当前运行入口文件
MAIN_NAME = os.path.split(os.path.splitext(sys.argv[0])[0])[-1]

# 当前运行路径
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 日志路径
LOG = 'log'
LOG_PATH = os.path.join(ROOT_PATH, LOG)

# 配置路径
CONFIG = 'conf'
CONFIG_PATH = os.path.join(ROOT_PATH, CONFIG)

# 配置文件路径
CONFIG_FILE = f"{PROJECT_NAME.lower()}.conf"
CONFIG_FILE_PATH = os.path.join(CONFIG_PATH, CONFIG_FILE)

# 模版文件路径
TEMPLATE = 'template'
TEMPLATE_PATH = os.path.join(ROOT_PATH, TEMPLATE)

# 静态文件路径
STATIC = 'static'
STATIC_PATH = os.path.join(ROOT_PATH, STATIC)

# WEB 调试模式
WEB_DEBUG = False

# 静态文件缓存
SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=1)

# Web 路径前缀
PREFIX_URL = "/" + PROJECT_NAME.lower()