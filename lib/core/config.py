#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from lib.core.env import *
import json
import configparser
from attribdict import AttribDict
from lib.util.util import random_string

def config_parser():
    """解析配置文件，如不存在则创建"""

    if not os.path.exists(CONFIG_FILE_PATH):
        init_conf(CONFIG_FILE_PATH)
        exit(f"Please set the {PROJECT_NAME} config in {CONFIG_FILE_PATH}...")

    config = load_conf(CONFIG_FILE_PATH)

    return config


def load_conf(path):
    """加载配置文件"""

    config = AttribDict()
    cf = configparser.ConfigParser()
    cf.read(path)
    sections = cf.sections()
    for section in sections:
        config[section] = AttribDict()
        for option in cf.options(section):
            value = cf.get(section, option)
            try:
                if value.startswith("{") and value.endswith("}") or value.startswith("[") and value.endswith("]"):
                    value = json.loads(value)
                elif value.lower() == "false":
                    value = False
                elif value.lower() == "true":
                    value = True
                else:
                    value = int(value)
            except Exception as e:
                pass
            config[section][option] = value
    return config


def init_conf(path):
    """初始化配置文件"""

    if not os.path.exists(CONFIG_PATH):
        os.mkdir(CONFIG_PATH)

    configs = {
        ("basic", f"This is a basic config for {PROJECT_NAME}"): {
            ("timeout", "Connection timeout"): 5,
            ("heartbeat_time", ""): 60,
            ("secret_key", "Secret key"): random_string(64),
            ("dingding_robot_url", "dingding robot url"): "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxx",
        },
        ("mysql", f"This is a mysql config for {PROJECT_NAME}"): {
            ("host", ""): "127.0.0.1",
            ("port", ""): 3306,
            ("username", ""): "root",
            ("password", ""): "123456",
            ("dbname", ""): PROJECT_NAME.lower(),
            ("charset", ""): "utf8mb4",
            ("collate", ""): "utf8mb4_general_ci",
        },
        ("manager", f"This is a manager config for {PROJECT_NAME}"): {
            ("listen_host", ""): "0.0.0.0",
            ("listen_port", ""): "8000",
            ("default_mail_siffix", ""): f"@{PROJECT_NAME.lower()}.com",
            ("default_password", ""): f"{PROJECT_NAME}@123",
        },
        ("dnslog", f"This is a dnslog config for {PROJECT_NAME}"): {
            ("listen_host", ""): "0.0.0.0",
            ("listen_port", ""): "53",
            ("ns1_domain", "A.com的域名的NS记录"): 'ns1.A.com',
            ("ns2_domain", "A.com的域名的NS记录"): 'ns2.A.com',
            ("dns_domain", "B.com，主要做DNS记录"): 'B.com',
            ("default_server_ip", "B.com 的默认解析地址"): '127.0.0.1',
            ("admin_domain", "admin管理的域名"): 'admin.B.com',
            ("admin_server_ip", "admin域名解析地址"): '127.0.0.1',
        },
    }

    cf = configparser.ConfigParser(allow_no_value=True)
    for (section, section_comment), section_value in configs.items():
        cf.add_section(section)

        if section_comment and section_comment != "":
            cf.set(section, fix_comment_content(f"{section_comment}\r\n"))

        for (key, key_comment), key_value in section_value.items():
            if key_comment and key_comment != "":
                cf.set(section, fix_comment_content(key_comment))
            if isinstance(key_value, dict) or isinstance(key_value, list):
                key_value = json.dumps(key_value)
            else:
                key_value = str(key_value)
            cf.set(section, key, f"{key_value}\r\n")

    with open(path, 'w+') as configfile:
        cf.write(configfile)


def fix_comment_content(content):
    """按照80个字符一行就行格式化处理"""

    text = f'; '
    for i in range(0, len(content)):
        if i != 0 and i % 80 == 0:
            text += '\r\n; '
        text += content[i]
    return text
