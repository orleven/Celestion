#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import json
from flask import request
from flask import render_template
from flask import Blueprint
from flask import session
from sqlalchemy import and_
from lib.core.env import *
from lib.hander import db
from lib.core.model import ResponseSetting
from lib.core.enums import ApiStatus
from lib.util.util import get_time
from lib.hander.basehander import save_sql
from lib.hander.basehander import fix_response
from lib.hander.basehander import login_check

mod = Blueprint('response', __name__, url_prefix=f'{PREFIX_URL}/response')

@mod.route('/index', methods=['POST', 'GET'])
@login_check
def response_index():
    ctx = {}
    ctx['title'] = 'Response'
    ctx['username'] = session.get('username')
    return render_template('manager/setting/response.html', **ctx)

@mod.route('/list', methods=['POST', 'GET'])
@login_check
@fix_response
def response_list():
    response = {
        'data': {
            'res': [],
            'total': 0,
        }
    }
    page = request.json.get('page', 1)
    per_page = request.json.get('per_page', 10)
    name = request.json.get('name', '')
    path = request.json.get('path', '')
    response_status_code = request.json.get('response_status_code', '')
    response_headers = request.json.get('response_headers', '')
    response_content = request.json.get('response_content', '')
    response_content_type = request.json.get('response_content_type', '')

    condition = (1 == 1)
    if name != '':
        condition = and_(condition, ResponseSetting.name.like('%' + name + '%'))

    if response_content_type != '':
        condition = and_(condition, ResponseSetting.response_content_type.like('%' + response_content_type + '%'))

    if path != '':
        condition = and_(condition, ResponseSetting.path.like('%' + path + '%'))

    if response_status_code != '':
        condition = and_(condition, ResponseSetting.response_status_code == response_status_code)

    if response_headers != '':
        condition = and_(condition, ResponseSetting.response_headers.like('%' + response_headers + '%'))

    if response_content != '':
        condition = and_(condition, ResponseSetting.request_content.like(bytes('%' + response_content + '%', encoding="utf8")))

    if per_page == 'all':
        for row in db.session.query(ResponseSetting).filter(condition).order_by(ResponseSetting.update_time.desc()).all():
            response['data']['res'].append(row.to_json())
    else:
        for row in db.session.query(ResponseSetting).filter(condition).order_by(ResponseSetting.update_time.desc()).paginate(page=page, per_page=per_page).items:
            response['data']['res'].append(row.to_json())
    response['data']['total'] = db.session.query(ResponseSetting).filter(condition).count()
    return response


@mod.route('/edit', methods=['POST', 'GET'])
@login_check
@fix_response
def response_edit():
    response_id = request.json.get('id', '')
    name = request.json.get('name', '')
    path = request.json.get('path', '')
    response_status_code = request.json.get('response_status_code', '')
    response_headers = request.json.get('response_headers', '')
    response_content = request.json.get('response_content', '')
    response_content_type = request.json.get('response_content_type', '')
    response_reason = request.json.get('response_reason', '')
    mark = request.json.get('mark', '')

    if response_id != '':
        response_id = int(response_id)
        response_setting = db.session.query(ResponseSetting).filter(ResponseSetting.id == response_id).first()
        if response_setting:
            response_setting.mark = mark
            try:
                response_headers = json.loads(response_headers)
                response_headers = json.dumps(response_headers)
            except:
                return ApiStatus.ERROR_INVALID_INPUT
            response_setting.response_headers = response_headers

            response_setting.response_status_code = int(response_status_code)
            response_setting.response_reason = response_reason
            response_setting.response_content = bytes(response_content, 'utf-8')
            response_setting.response_content_type = response_content_type
            response_setting.path = path
            response_setting.name = name
            response_setting.update_time = get_time()
            save_sql(response_setting)
            return {'data': {'res': [response_id]}}
    return ApiStatus.ERROR_IS_NOT_EXIST


@mod.route('/add', methods=['POST', 'GET'])
@login_check
@fix_response
def response_add():
    name = request.json.get('name', '')
    path = request.json.get('path', '')
    response_status_code = request.json.get('response_status_code', 200)
    response_headers = request.json.get('response_headers', '{}')
    response_content = request.json.get('response_content', '')
    response_content_type = request.json.get('response_content_type', 'text/plain;charset=UTF-8')
    response_reason = request.json.get('response_reason', 'OK')
    mark = request.json.get('mark', '')

    if name == '':
        return ApiStatus.ERROR_INVALID_INPUT

    try:
        response_headers = json.loads(response_headers)
        response_headers = json.dumps(response_headers)
    except:
        return ApiStatus.ERROR_INVALID_INPUT


    response_status_code = int(response_status_code)
    response_content = bytes(response_content, 'utf-8')

    update_time = get_time()

    response_setting = ResponseSetting(name=name, path=path, response_status_code=response_status_code, mark=mark,
                                       response_content=response_content, response_headers=response_headers,
                                       response_reason=response_reason, response_content_type=response_content_type,
                                       update_time=update_time)
    save_sql(response_setting)
    return {'data': {'res': [name]}}

@mod.route('/delete', methods=['POST', 'GET'])
@login_check
@fix_response
def response_delete():
    response = {'data': {'res': []}}
    response_id = request.json.get('id', '')
    response_ids = request.json.get('ids', '')
    if response_id != '' or response_ids != '':
        if response_id != '':
            response = db.session.query(ResponseSetting).filter(ResponseSetting.id == response_id).first()
            if response:
                db.session.delete(response)
                db.session.commit()
                response['data']['res'].append(response_id)
        elif response_ids != '':
            try:
                for response_id in response_ids.split(','):
                    response_id = response_id.replace(' ', '')
                    response = db.session.query(ResponseSetting).filter(ResponseSetting.id == response_id).first()
                    if response:
                        db.session.delete(response)
                        db.session.commit()
                        response['data']['res'].append(response_id)
            except:
                pass
        return response
    return ApiStatus.ERROR_IS_NOT_EXIST
