#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import json
from sqlalchemy import and_
from flask import request
from flask import Blueprint
from lib.core.enums import API_STATUS
from lib.core.model import DNSLog
from lib.core.model import WebLog
from lib.handers import db
from lib.handers.basehander import fix_response
from lib.handers.basehander import login_check

mod = Blueprint('api', __name__, url_prefix='/api')

@mod.route('/dnslog/list', methods=['POST', 'GET'])
@login_check
@fix_response
def api_dnslog_list():
    """获取dnslog信息"""
    response = {
        'data': {
            'res': [],
            'total': 0,
        }
    }
    page = request.json.get('page', 1)
    per_page = request.json.get('per_page', 10)
    domain = request.json.get('domain', '')
    ip = request.json.get('ip', '')
    condition = (1 == 1)

    if ip != '':
        condition = and_(condition, DNSLog.ip == ip)

    if domain != '':
        condition = and_(condition, DNSLog.domain == domain)

    if per_page == 'all':
        for row in db.session.query(DNSLog).filter(condition).all():
            response['data']['res'].append(row.to_json())
    else:
        for row in db.session.query(DNSLog).filter(condition).order_by(
                DNSLog.update_time.desc()).paginate(page=page, per_page=per_page).items:
            response['data']['res'].append(row.to_json())

    response['data']['total'] = db.session.query(DNSLog).filter(condition).count()
    return response

@mod.route('/dnslog/detail', methods=['POST', 'GET'])
@login_check
@fix_response
def api_dnslog_detail():
    """获取dnslog信息"""
    response = {'data': {'res': []}}
    dnslog_id = request.json.get('id', '')
    if dnslog_id != '':
        dnslog = db.session.query(WebLog).filter(WebLog.id == dnslog_id).first()
        if dnslog:
            response['data']['res'].append(dnslog.to_json())
            response['data']['total'] = 1
    return response

@mod.route('/weblog/list', methods=['POST', 'GET'])
@login_check
@fix_response
def api_weblog_list():
    """获取weblog信息"""
    response = {
        'data': {
            'res': [],
            'total': 0,
        }
    }
    page = request.json.get('page', 1)
    per_page = request.json.get('per_page', 10)
    ip = request.json.get('ip', '')
    url = request.json.get('url', '')
    condition = (1 == 1)

    if ip != '':
        condition = and_(condition, WebLog.ip == ip)
    if url != '':
        condition = and_(condition, WebLog.url.like('%' + url + '%'))

    if per_page == 'all':
        for row in db.session.query(WebLog).filter(condition).all():
            response['data']['res'].append(row.to_json())
    else:
        for row in db.session.query(WebLog).filter(condition).order_by(
                WebLog.update_time.desc()).paginate(page=page, per_page=per_page).items:
            response['data']['res'].append(row.to_json())

    response['data']['total'] = db.session.query(WebLog).filter(condition).count()
    return response


@mod.route('/weblog/detail', methods=['POST', 'GET'])
@login_check
@fix_response
def api_weblog_detail():
    """获取weblog信息"""
    response = {'data': {'res': []}}
    weblog_id = request.json.get('id', '')
    if weblog_id != '':
        weblog = db.session.query(WebLog).filter(WebLog.id == weblog_id).first()
        if weblog:
            weblog_dic = {}
            request_headers = json.loads(weblog.request_headers)
            url_temp = weblog.url[weblog.url.replace('://', '___').index('/'):]
            weblog_dic['url'] = weblog.url
            weblog_dic['request'] = weblog.method + ' ' + url_temp + ' ' + weblog.request_http_version + '\r\n'
            weblog_dic['request'] += '\r\n'.join([key + ': ' + value for key, value in request_headers.items()])
            weblog_dic['request'] += '\r\n\r\n'
            weblog_dic['request'] += bytes.decode(weblog.request_content)
            response['data']['res'].append(weblog_dic)
        return response
    return API_STATUS.ERROR_IS_NOT_EXIST

