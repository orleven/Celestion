#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import multiprocessing
from lib.handers import app
from werkzeug.middleware.proxy_fix import ProxyFix
from lib.core.dnsserver import dns_server

def start(args):
    try:
        p = multiprocessing.Process(target=start_dns_server, args=(args.listen_dns_host, args.listen_dns_port))
        p.daemon = True
        p.start()

        app.wsgi_app = ProxyFix(app.wsgi_app)
        app.run(host=args.listen_host, port=args.listen_port)
    except KeyboardInterrupt:
        exit(0)

def start_dns_server(address='0.0.0.0', port=53):
    dns_server(address, port)
