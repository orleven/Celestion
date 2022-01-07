#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import json
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers.response import Response
from flask import request
from flask import jsonify
from flask import Blueprint
from flask import session
from flask import redirect
from sqlalchemy import or_
from functools import wraps
from lib.handers import app
from lib.handers import db
from lib.core.data import access_log
from lib.core.data import cache_log
from lib.core.data import log
from lib.core.data import msg_queue
from lib.core.config import BaseConfig
from lib.core.config import Config
from lib.core.model import User
from lib.core.model import WebLog
from lib.core.model import ResponseSetting
from lib.core.model import Log
from lib.core.enums import API_STATUS
from lib.core.enums import LOG_TYPE
from lib.core.enums import ROLE
from lib.core.enums import USER_STATUS
from lib.utils.util import parser_header
from lib.utils.util import get_safe_ex_string
from lib.utils.util import get_time

mod = Blueprint('base', __name__, url_prefix='/')


class WebDomainResponse(HTTPException):

    def recode_request(self, resp):
        url = request.url
        method = request.method
        protocol = request.environ.get('SERVER_PROTOCOL')
        ip = request.remote_addr
        request_content = request.stream.read()
        request_content_length = len(request_content)
        dns_domain = BaseConfig.DNS_DOMAIN
        address = request.host.split(':')
        host = address[0]
        port = address[1] if len(address) == 2 else "80"
        scheme = 'http'
        request_headers = json.dumps(parser_header(request.headers, False))
        response_reason = resp.status[resp.status.index(' '):]
        response_status_code = resp.status_code
        response_headers = json.dumps(parser_header(resp.headers, False))
        response_content_type = resp.headers["Content-Type"] if "Content-Type" in resp.headers else None
        response_content = resp.data

        update_time = get_time()
        weblog = WebLog(ip=ip, request_content_length=request_content_length, request_content=request_content,
                        request_headers=request_headers, update_time=update_time, url=url, host=host, port=port,
                        scheme=scheme, dns_domain=dns_domain, request_http_version=protocol, method=method,
                        response_reason=response_reason, response_status_code=response_status_code, response_headers=response_headers,
                        response_content_type=response_content_type, response_content=response_content)
        save_sql(weblog)
        cache_log.info(f'ip: {ip}, method: {method} url: {url}, headers: {request_headers}, data: {request_content}')

        msg = f'WEBLOG 上线\nurl: {url}\nip: {ip}\nheaders: {request_headers}\nbody: {request_content}\ntime: {update_time}'
        msg_queue.put(msg)

    def get_response(self, environ=None, scope = None):
        path = request.path
        resp = Response(b"", 200, [])
        response_setting = db.session.query(ResponseSetting).filter(or_(ResponseSetting.path == path)).first()
        if response_setting is None:
            response_setting = db.session.query(ResponseSetting).filter(or_(ResponseSetting.path == "")).first()

        if response_setting:
            if response_setting.response_headers:
                for key, value in resp.headers.items():
                    del resp.headers[key]
                for key, value in json.loads(response_setting.response_headers).items():
                    resp.headers[key] = value
            if response_setting.response_content_type:
                resp.headers["Content-Type"] = response_setting.response_content_type
            if response_setting.response_content:
                resp.data = response_setting.response_content
                resp.headers["Content-Length"] = len(response_setting.response_content)
            if response_setting.response_status_code:
                resp.status_code = response_setting.response_status_code
            if response_setting.response_reason:
                resp.status = f'{resp.status_code} {response_setting.response_reason}'

        self.recode_request(resp)

        return resp


def fix_response(func):
    """
    统一返回的json，补充有status以及msg字段
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        status = API_STATUS.SUCCESS['status']
        msg = API_STATUS.SUCCESS['msg']
        if isinstance(ret, dict):
            if 'status' in ret.keys() and ret['status'] != status:
                status = ret['status']
            if 'msg' in ret.keys() and ret['msg'] != msg:
                msg = ret['msg']
            ret['status'] = status
            ret['msg'] = msg
            return jsonify(ret)
        else:
            pass

    return wrapper


def login_check(func):
    """
    权限简单校验，防止未授权
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        if request.path in ['/login', '/logout']:
            pass

        elif request.path.startswith('/' + Config.STATICS):
            pass

        elif request.path.startswith("/api/"):
            api_key = request.headers.get('API-Key', '')

            # 只收json格式
            if request.json == None:
                return jsonify(API_STATUS.ERROR_ILLEGAL_PROTOCOL)

            # api 访问使用api-key
            elif api_key == None or api_key == '':
                return jsonify(API_STATUS.ERROR_INVALID_API_KEY)

            else:
                user = db.session.query(User).filter(or_(User.api_key == api_key)).first()
                if user != None:
                    if user.to_json()['status'] != USER_STATUS.OK:
                        return jsonify(API_STATUS.ERROR_ACCOUNT)
                    else:
                        user.login_time = get_time()
                        save_sql(user)
                else:
                    return jsonify(API_STATUS.ERROR_INVALID_API_KEY)

        else:
            user_token = session.get('user')
            if user_token != None:
                user = User.verify_auth_token(user_token)
                if user != None:
                    user_dict = user.to_json()

                    # 账号被ban
                    if user_dict['status'] != USER_STATUS.OK:
                        return jsonify(API_STATUS.ERROR_ACCOUNT)

                    else:
                        if user_dict['role'] not in [ROLE.GUEST, ROLE.ADMIN, ROLE.USER]:
                            return jsonify(API_STATUS.ERROR_ACCOUNT)

                        ip = request.remote_addr
                        log_type = LOG_TYPE.LOGIN  # 日志类型
                        description = str(request.json)
                        url = request.path
                        update_time = get_time()
                        log = Log(ip=ip, log_type=log_type, description=description, url=url, user=user,
                                  update_time=update_time)
                        save_sql(log)
                else:
                    return redirect('/login')
            else:
                return redirect('/login')
        return func(*args, **kwargs)

    return wrapper


@app.errorhandler(400)
def error_400(error):
    return jsonify(API_STATUS.ERROR_400), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify(API_STATUS.ERROR_404), 404

@app.errorhandler(500)
def error_500(error):
    return jsonify(API_STATUS.ERROR_500), 500

@app.before_request
def before_request():
    # 返回自定义页面
    host = request.host if ':' not in request.host else request.host.split(':')[0]
    if host == BaseConfig.ADMIN_DOMAIN:
        pass
    else:
        return WebDomainResponse()


@app.after_request
def after_request(resp):
    host = request.host if ':' not in request.host else request.host.split(':')[0]
    if host == BaseConfig.ADMIN_DOMAIN:
        resp.headers.set("Server", Config.VERSION_STRING)
        resp.headers.set("X-XSS-Protection", "1; mode=block")
        resp.headers.set("X-Frame-Options", "DENY")
        resp.headers.set("X-Content-Type-Options", "nosniff")


    ip = request.remote_addr
    ua = request.user_agent.string

    url = request.url
    method = request.method
    status_code = resp.status_code
    content_length = resp.headers.get('Content-Length', 0)
    referrer = request.referrer if request.referrer != None else "-"
    protocol = request.environ.get('SERVER_PROTOCOL')
    x_forwarded_for = request.headers.get('X-Forwarded-For', '"-"')
    access_log.info(f'{ip} "{method} {url} {protocol}" {status_code} {content_length} "{referrer}" "{ua}" {x_forwarded_for}')
    return resp

def save_sql(item):
    db.session.add(item)
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        if 'PRIMARY' in str(e):
            return True
        log.error("Insert error: {}".format(get_safe_ex_string(e)))
    return False

