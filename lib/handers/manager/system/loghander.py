#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from flask import request
from flask import render_template
from flask import Blueprint
from flask import session
from sqlalchemy import and_
from sqlalchemy import or_
from lib.core.model import Log
from lib.core.model import User
from lib.handers import db
from lib.utils.util import get_timestamp
from lib.utils.util import get_time
from lib.handers.basehander import save_sql
from lib.core.enums import API_STATUS
from lib.core.enums import LOG_STATUS
from lib.core.enums import LOG_TYPE
from lib.handers.basehander import fix_response
from lib.handers.basehander import login_check

mod = Blueprint('log', __name__, url_prefix='/log')

@mod.route('/index', methods=['POST', 'GET'])
@login_check
def log_index():
    ctx = {}
    ctx['title'] = 'Log'
    ctx['username'] = session.get('username')
    ctx['log_type'] = LOG_TYPE
    return render_template('manager/system/log.html', **ctx)


@mod.route('/list', methods=['POST', 'GET'])
@login_check
@fix_response
def log_list():
    response = {
        'data': {
            'res': [],
            'total': 0,
        }
    }
    page = request.json.get('page', 1)
    per_page = request.json.get('per_page', 10)
    update_time = request.json.get('update_time', '')
    url = request.json.get('url', '')
    ip = request.json.get('ip', '')
    user = request.json.get('user', '')
    condition = (Log.status == LOG_STATUS.OK)
    if update_time != '':
        condition = and_(condition, Log.update_time.like('%' + update_time + '%'))

    if url != '':
        condition = and_(condition, Log.url.like('%' + url + '%'))

    if user != '':
        users = db.session.query(User).filter(User.username.like('%' + user + '%')).all()
        condition_user = (1 == 2)
        for user in users:
            condition_user = or_(condition_user, Log.user_id == user.id)
        condition = and_(condition, condition_user)

    if ip != '':
        condition = and_(condition, Log.body.like('%' + ip + '%'))

    if per_page == 'all':
        for row in db.session.query(Log).filter(condition).all():
            response['data']['res'].append(row.to_json())
    else:
        for row in db.session.query(Log).filter(condition).order_by(Log.update_time.desc()).paginate(page=page, per_page=per_page).items:
            response['data']['res'].append(row.to_json())
    response['data']['total'] = db.session.query(Log).filter(condition).count()
    return response

@mod.route('/clear_all', methods=['POST', 'GET'])
@login_check
@fix_response
def log_clear_all():
    response = {'data': {'res': []}}
    delete_time = get_time(get_timestamp()- 60 * 60 * 24 * 7)
    condition = (Log.status == LOG_STATUS.OK)
    condition = and_(condition, Log.update_time <= delete_time)
    for row in db.session.query(Log).filter(condition).all():
        row.status = LOG_STATUS.DELETE
        save_sql(row)
    return response

@mod.route('/delete', methods=['POST', 'GET'])
@login_check
@fix_response
def log_delete():
    response = {'data': {'res': []}}
    log_id = request.json.get('id', '')
    log_ids = request.json.get('ids', '')
    if log_id != '' or log_ids != '':
        if log_id != '':
            log_id = int(log_id)
            log = db.session.query(Log).filter(Log.id == log_id).first()
            if log:
                log.status = LOG_STATUS.DELETE
                save_sql(log)
                response['data']['res'].append(log_id)
        if log_ids != '':
            try:
                for log_id in log_ids.split(','):
                    log_id = int(log_id.replace(' ', ''))
                    log = db.session.query(Log).filter(Log.id == log_id).first()
                    if log:
                        log.status = LOG_STATUS.DELETE
                        save_sql(log)
                        response['data']['res'].append(log_id)
            except:
                pass
        return response
    return API_STATUS.ERROR_IS_NOT_EXIST