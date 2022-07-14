#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from lib.core.env import *
from argparse import ArgumentParser
from lib.core.core import start

def arg_set(parser):
    parser.add_argument('-l', "--listen_host", type=str, help='Web listen host')
    parser.add_argument('-p', "--listen_port", type=int, help='Web listen port')
    parser.add_argument('-dl', "--listen_dns_host", type=str, help='DNS listen host')
    parser.add_argument('-dp', "--listen_dns_port", type=int, help='DNS listen port')
    parser.add_argument("-d", "--debug", action='store_true', help="Run debug model", default=False)
    parser.add_argument("--help", help="Show help", default=False, action='store_true')
    return parser

if __name__ == '__main__':
    parser = ArgumentParser(add_help=False)
    parser = arg_set(parser)
    args = parser.parse_args()
    if args.help:
        parser.print_help()
    else:
        start(args)
