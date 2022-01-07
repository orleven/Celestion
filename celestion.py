#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from argparse import ArgumentParser
from lib.core.config import Config
from lib.core.core import start
from lib.core.data import log
from lib.core.enums import CUSTOM_LOGGING

if __name__ == "__main__":
    parser = ArgumentParser(description=Config.DESCRIPTION, add_help=False)
    parser.add_argument('-l', "--listen_host", type=str, default="127.0.0.1", help='Web listen host')
    parser.add_argument('-p', "--listen_port", type=int, default=8000, help='Web listen port')
    parser.add_argument('-dl', "--listen_dns_host", type=str, default="0.0.0.0", help='DNS listen host')
    parser.add_argument('-dp', "--listen_dns_port", type=int, default=53, help='DNS listen port')
    parser.add_argument("-d", "--debug", action='store_true', help="Run debug model", default=False)
    parser.add_argument("--help", help="Show help", default=False, action='store_true')
    args = parser.parse_args()
    if args.debug:
        log.set_level(CUSTOM_LOGGING.DEBUG)
    if args.help:
        parser.print_help()
    else:
        start(args)