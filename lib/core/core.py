#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from lib.core.env import *
import multiprocessing
from lib.core.enums import CustomLogging
from lib.hander import app
from lib.core.g import conf
from lib.core.g import cache_log
from lib.core.g import log
from werkzeug.middleware.proxy_fix import ProxyFix
from lib.core.dnsserver import dns_server


def handle_options(args):
    """参数解析与配置"""

    if hasattr(args, "listen_host") and args.listen_host:
        conf.manager.listen_host = args.listen_host

    if hasattr(args, "listen_port") and args.listen_port:
        conf.manager.listen_port = args.listen_port

    if hasattr(args, "listen_dns_host") and args.listen_dns_host:
        conf.dnslog.listen_host = args.listen_dns_host

    if hasattr(args, "listen_dns_port") and args.listen_dns_port:
        conf.dnslog.listen_port = args.listen_dns_port

    # debug 模式
    conf.basic.debug = args.debug

    if conf.basic.debug:
        log_level = CustomLogging.DEBUG
        log.set_level(log_level)
        cache_log.set_level(log_level)
        log.debug(f"Setting {PROJECT_NAME} debug mode...")


def start(args):
    handle_options(args)
    try:
        p = multiprocessing.Process(target=start_dns_server)
        p.daemon = True
        p.start()
        app.wsgi_app = ProxyFix(app.wsgi_app)
        app.run(host=conf.manager.listen_host, port=conf.manager.listen_port)
    except KeyboardInterrupt:
        exit(0)

def start_dns_server(address=conf.dnslog.listen_host, port=conf.dnslog.listen_port):
    dns_server(address, port)
