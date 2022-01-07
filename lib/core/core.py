#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import time
import threading
import multiprocessing
from lib.handers import app
from lib.core.data import msg_queue
from lib.core.data import log
from werkzeug.middleware.proxy_fix import ProxyFix
from lib.core.dnsserver import dns_server
from lib.utils.util import seng_message


def start(args):
    try:
        p = multiprocessing.Process(target=start_dns_server, args=(args.listen_dns_host, args.listen_dns_port))
        p.daemon = True
        p.start()

        t = threading.Thread(target=start_msg_center)
        t.start()

        app.wsgi_app = ProxyFix(app.wsgi_app)
        app.run(host=args.listen_host, port=args.listen_port)
    except KeyboardInterrupt:
        exit(0)

def start_dns_server(address='0.0.0.0', port=53):
    dns_server(address, port)

def start_msg_center():
    while True:
        if msg_queue.qsize() > 0:
            msg = msg_queue.get()
            flag, err = seng_message(msg)
            msg = msg.replace('\n', ', ').replace('\r', ', ')
            if flag:
                log.success(f'Send message to IM, msg: {msg}')
            else:
                log.error(f'Send message to IM error, msg: {msg}, error: {err}')
        time.sleep(0.1)