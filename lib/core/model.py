#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from datetime import datetime
from flask_login import UserMixin
from lib.core.enums import LogStatus
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import BLOB
from sqlalchemy import BOOLEAN
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from lib.core.g import engine
from lib.core.g import conf
from lib.util.util import get_time
from lib.util.util import get_timedelta
from lib.util.cipherutil import jwtdecode
from lib.util.cipherutil import jwtencode


Base = declarative_base(engine)

class DNSSetting(Base):
    """DNSSetting"""
    __tablename__ = "dns_setting"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(255))
    mark = Column(Text())
    domain = Column(String(255))
    value1 = Column(String(255))
    value2 = Column(String(255))
    dns_domain = Column(String(255), default=conf.dnslog.dns_domain)
    dns_redirect = Column(BOOLEAN(), default=False)
    type = Column(String(255), default='A')
    update_time = Column(DateTime())

    def to_json(self):
        json_data = {
            'id': self.id,
            "name": self.name,
            "mark": self.mark,
            "domain": self.domain,
            "value1": self.value1,
            "value2": self.value2,
            "dns_redirect": self.dns_redirect,
            "dns_domain": self.dns_domain,
            "type": self.type,
            'update_time': datetime.strftime(self.update_time, "%Y-%m-%d %H:%M:%S"),
        }
        return json_data

class ResponseSetting(Base):
    """ResponseSetting"""
    __tablename__ = "response_setting"
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(255))
    mark = Column(Text())
    path = Column(Text())
    response_reason = Column(String(255))
    response_status_code = Column(Integer())
    response_headers = Column(Text())
    response_content_type = Column(String(255))
    response_content = Column(BLOB(131080))
    update_time = Column(DateTime())

    def to_json(self):
        json_data = {
            'id': self.id,
            "name": self.name,
            "mark": self.mark,
            "path": self.path,
            "response_reason": self.response_reason,
            "response_status_code": self.response_status_code,
            "response_headers": self.response_headers,
            "response_content_type": self.response_content_type,
            "response_content": str(self.response_content, 'utf-8'),
            'update_time': datetime.strftime(self.update_time, "%Y-%m-%d %H:%M:%S"),
        }
        return json_data

class DNSLog(Base):
    """DNSLog"""
    __tablename__ = "dnslog"  # 指明数据库表名
    id = Column(Integer(), primary_key=True, autoincrement=True)  # 主键 整型的主键默认设置为自增
    domain = Column(String(255))
    ip = Column(String(255))
    dns_domain = Column(String(255))
    type = Column(String(255))
    update_time = Column(DateTime())

    def to_json(self):
        json_data = {
            'id': self.id,
            "domain": self.domain,
            "ip": self.ip,
            "dns_domain": self.dns_domain,
            "type": self.type,
            'update_time': datetime.strftime(self.update_time, "%Y-%m-%d %H:%M:%S"),
        }
        return json_data

class WebLog(Base):
    """WebLog"""
    __tablename__ = "weblog"  # 指明数据库表名
    id = Column(Integer(), primary_key=True, autoincrement=True)  # 主键 整型的主键默认设置为自增
    dns_domain = Column(String(255))
    scheme = Column(String(255))
    method = Column(String(255))
    host = Column(String(255))
    port = Column(Integer())
    url = Column(Text())

    request_http_version = Column(String(255))
    request_headers = Column(Text())
    request_content_length = Column(Integer())
    request_content = Column(BLOB(131080))

    response_reason = Column(String(255))
    response_status_code = Column(Integer())
    response_headers = Column(Text())
    response_content_type = Column(String(255))
    response_content = Column(BLOB(131080))

    ip = Column(String(255))

    update_time = Column(DateTime())

    def to_json(self):
        json_data = {
            'id': self.id,
            "scheme": self.scheme,
            "method": self.method,
            "host": self.host,
            "port": self.port,
            "url": self.url,
            "dns_domain": self.dns_domain,
            'request_http_version': self.request_http_version,
            "request_headers": self.request_headers,
            "request_content_length": self.request_content_length,
            # "request_content": self.request_content,
            "response_reason": self.response_reason,
            "response_status_code": self.response_status_code,
            "response_headers": self.response_headers,
            "response_content_type": self.response_content_type,
            # "response_content": self.response_content,
            'update_time': datetime.strftime(self.update_time, "%Y-%m-%d %H:%M:%S"),
            "ip": self.ip,
        }
        return json_data


class Log(Base):
    """Log"""
    __tablename__ = "log"  # 指明数据库表名
    id = Column(Integer(), primary_key=True, autoincrement=True)  # 主键 整型的主键默认设置为自增
    ip = Column(String(40))  # 日志产生IP
    log_type = Column(String(255))  # 日志类型
    description = Column(Text())
    status = Column(String(40), default=LogStatus.OK)  # 日志状态，0为逻辑删除
    url = Column(Text())
    update_time = Column(DateTime())

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User')

    def to_json(self):
        json_data = {
            'id': self.id,
            'ip': self.ip,
            'log_type': self.log_type,
            'description': self.description,
            'url': self.url,
            'update_time': datetime.strftime(self.update_time, "%Y-%m-%d %H:%M:%S"),
            'user': self.user.username if self.user is not None else self.user,
            'user_id': self.user_id,
        }
        return json_data


class User(UserMixin, Base):
    """User 账户测试用"""
    __tablename__ = "user"  # 指明数据库表名
    id = Column(Integer(), primary_key=True, autoincrement='ignore_fk')
    email = Column(String(255), unique=True)  # 唯一性
    username = Column(String(255))
    description = Column(Text())
    password = Column(String(255))
    status = Column(String(255))
    role = Column(String(255))
    login_failed = Column(Integer())
    failed_time = Column(DateTime())
    created_time = Column(DateTime())
    login_time = Column(DateTime())
    update_time = Column(DateTime())
    api_key = Column(String(255))
    mark = Column(Text())

    def to_json(self):
        json_data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'description': self.description,
            'status': self.status,
            'login_failed': self.login_failed,
            'failed_time': datetime.strftime(self.failed_time, '%Y-%m-%d %H:%M:%S') if self.failed_time else None,
            'created_time': datetime.strftime(self.created_time, "%Y-%m-%d %H:%M:%S") if self.created_time else None,
            'login_time': datetime.strftime(self.login_time, "%Y-%m-%d %H:%M:%S") if self.login_time else None,
            'update_time': datetime.strftime(self.login_time, "%Y-%m-%d %H:%M:%S")if self.login_time else None,
            'mark': self.mark,
        }
        return json_data

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def generate_password_hash(self, password=None):
        if password is None:
            password = self.password
        return generate_password_hash(password)

    def generate_auth_token(self, expiration=3600):
        message = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "status": self.status,
            "role": self.role,
            "exp": get_time() + get_timedelta(seconds=expiration)
        }
        token = jwtencode(message, conf.basic.secret_key, algorithm="HS256")
        return token

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwtdecode(token, conf.basic.secret_key, algorithms=["HS256"], do_time_check=True)
            if data and isinstance(data, dict):
                from lib.hander import db
                return db.session.query(User).get(data["id"])
        except:
            return None
        return None
