#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import json
from flask import request
from flask import render_template
from flask import Blueprint
from flask import session
from sqlalchemy import and_
from lib.handers import db
from lib.core.model import WebLog
from lib.core.enums import API_STATUS
from lib.utils.util import get_timestamp
from lib.utils.util import get_time
from lib.handers.basehander import fix_response
from lib.handers.basehander import login_check

mod = Blueprint('weblog', __name__, url_prefix='/weblog')


@mod.route('/index', methods=['POST', 'GET'])
@login_check
def weblog_index():
    ctx = {}
    ctx['title'] = 'WebLog'
    ctx['username'] = session.get('username')
    return render_template('manager/log/weblog.html', **ctx)

@mod.route('/list', methods=['POST', 'GET'])
@login_check
@fix_response
def weblog_list():
    response = {
        'data': {
            'res': [],
            'total': 0,
        }
    }
    page = request.json.get('page', 1)
    per_page = request.json.get('per_page', 10)
    url = request.json.get('url', '')
    request_headers = request.json.get('request_headers', '')
    request_content = request.json.get('request_content', '')
    method = request.json.get('method', '')
    response_status_code = request.json.get('status_code', '')
    condition = (1 == 1)

    if request_content != '':
        condition = and_(condition, WebLog.request_content.like(bytes('%' + request_content + '%', encoding="utf8")))

    if url != '':
        condition = and_(condition, WebLog.url.like('%' + url + '%'))

    if method != '':
        condition = and_(condition, WebLog.method.like('%' + method + '%'))

    if response_status_code != '':
        condition = and_(condition, WebLog.response_status_code.like('%' + response_status_code + '%'))

    if request_headers != '':
        condition = and_(condition, WebLog.request_headers.like('%' + request_headers + '%'))

    if per_page == 'all':
        for row in db.session.query(WebLog).filter(condition).order_by(WebLog.update_time.desc()).all():
            response['data']['res'].append(row.to_json())
    else:
        for row in db.session.query(WebLog).filter(condition).order_by(WebLog.update_time.desc()).paginate(page=page,
                                                                                               per_page=per_page).items:
            response['data']['res'].append(row.to_json())
    response['data']['total'] = db.session.query(WebLog).filter(condition).count()

    return response


@mod.route('/delete', methods=['POST', 'GET'])
@login_check
@fix_response
def weblog_delete():
    response = {'data': {'res': []}}
    weblog_id = request.json.get('id', '')
    weblog_ids = request.json.get('ids', '')
    if weblog_id != '' or weblog_ids != '':
        if weblog_id != '':
            weblog = db.session.query(WebLog).filter(WebLog.id == weblog_id).first()
            if weblog:
                db.session.delete(weblog)
                db.session.commit()
                response['data']['res'].append(weblog_id)
        if weblog_ids != '':
            try:
                for weblog_id in weblog_ids.split(','):
                    weblog_id = weblog_id.replace(' ', '')
                    weblog = db.session.query(WebLog).filter(WebLog.id == weblog_id).first()
                    if weblog:
                        db.session.delete(weblog)
                        db.session.commit()
                        response['data']['res'].append(weblog_id)
            except:
                pass
        return response
    return API_STATUS.ERROR_IS_NOT_EXIST


@mod.route('/detail', methods=['POST', 'GET'])
@login_check
@fix_response
def weblog_detail():
    response = {'data': {'res': []}}
    weblog_id = request.json.get('id', '')
    if weblog_id != '':
        weblog = db.session.query(WebLog).filter(WebLog.id == weblog_id).first()
        if weblog:
            weblog_dic = {}
            request_headers = json.loads(weblog.request_headers)
            response_headers = json.loads(weblog.response_headers)
            url_temp = weblog.url[weblog.url.replace('://', '___').index('/'):]
            weblog_dic['url'] = weblog.url
            weblog_dic['request'] = weblog.method + ' ' + url_temp + ' ' + weblog.request_http_version + '\r\n'
            weblog_dic['request'] += '\r\n'.join([key + ': ' + value for key, value in request_headers.items()])
            weblog_dic['request'] += '\r\n\r\n'
            weblog_dic['request'] += bytes.decode(weblog.request_content)

            weblog_dic['response'] = 'HTTP/1.0 ' + str(weblog.response_status_code) + ' ' + weblog.response_reason + '\r\n'
            weblog_dic['response'] += '\r\n'.join([key + ': ' + value for key, value in response_headers.items()])
            weblog_dic['response'] += '\r\n\r\n'
            weblog_dic['response'] += bytes.decode(weblog.response_content)
            response['data']['res'].append(weblog_dic)
        return response
    return API_STATUS.ERROR_IS_NOT_EXIST


@mod.route('/clear_old', methods=['POST', 'GET'])
@login_check
@fix_response
def weblog_clear_old():
    response = {'data': {'res': []}}
    delete_time = get_time(get_timestamp() - 60 * 60 * 24 * 3)
    condition = (1 == 1)
    condition = and_(condition, WebLog.update_time <= delete_time)
    db.session.query(WebLog).filter(condition).delete(synchronize_session=False)
    return response
