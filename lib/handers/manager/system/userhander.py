#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import re
from flask import request
from flask import render_template
from flask import Blueprint
from flask import session
from sqlalchemy import and_
from lib.handers import db
from lib.core.model import User
from lib.handers.basehander import save_sql
from lib.utils.util import get_time
from lib.core.enums import API_STATUS
from lib.core.enums import USER_STATUS
from lib.core.enums import ROLE
from lib.core.config import BaseConfig
from lib.utils.util import random_string
from lib.handers.basehander import fix_response
from lib.handers.basehander import login_check
from werkzeug.security import generate_password_hash

mod = Blueprint('user', __name__, url_prefix='/user')

@mod.route('/index', methods=['POST', 'GET'])
@login_check
def user_index():
    ctx = {}
    ctx['title'] = 'User'
    ctx['username'] = session.get('username')
    ctx['user_status'] = USER_STATUS
    return render_template('manager/system/user.html', **ctx)

@mod.route('/list', methods=['POST', 'GET'])
@login_check
@fix_response
def user_list():
    response = {
        'data': {
            'res': [],
            'total': 0,
        }
    }
    page = request.json.get('page', 1)
    per_page = request.json.get('per_page', 10)
    username = request.json.get('username', '')
    email = request.json.get('email', '')
    role = request.json.get('role', '')
    status = request.json.get('status', '')

    condition = (1 == 1)
    if username != '':
        condition = and_(condition, User.username.like('%' + username + '%'))

    if email != '':
        condition = and_(condition, User.email.like('%' + email + '%'))

    if status != '' and status in [USER_STATUS.OK, USER_STATUS.BAN]:
        condition = and_(condition, User.status == status)

    if role != '' and role in [ROLE.ADMIN, ROLE.GUEST, ROLE.USER]:
        condition = and_(condition, User.role == role)

    if per_page == 'all':
        for row in db.session.query(User).filter(condition).all():
            response['data']['res'].append(row.to_json())
    else:
        for row in db.session.query(User).filter(condition).order_by(User.update_time.desc()).paginate(page=page, per_page=per_page).items:
            response['data']['res'].append(row.to_json())
    response['data']['total'] = db.session.query(User).filter(condition).count()
    return response

@mod.route('/delete', methods=['POST', 'GET'])
@login_check
@fix_response
def user_delete():
    response = {'data': {'res': []}}
    user_id = request.json.get('id', '')
    user_ids = request.json.get('ids', '')
    if user_id != '' or user_ids != '':
        if user_id != '':
            user_id = int(user_id)
            user = db.session.query(User).filter(User.id == user_id).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                response['data']['res'].append(user_id)
        if user_ids != '':
            try:
                for user_id in user_ids.split(','):
                    user_id = int(user_id.replace(' ', ''))
                    user = db.session.query(User).filter(User.id == user_id).first()
                    if user:
                        db.session.delete(user)
                        db.session.commit()
                        response['data']['res'].append(user_id)
            except:
                pass
        return response
    return API_STATUS.ERROR_IS_NOT_EXIST

@mod.route('/add', methods=['POST', 'GET'])
@login_check
@fix_response
def user_add():
    email = request.json.get('email', '')
    username = request.json.get('username', '')
    mark = request.json.get('mark', '')
    role = request.json.get('role', '')
    description = request.json.get('description', '')
    if not re.match(r"^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9\-.]+)$", email):
        return API_STATUS.ERROR_INVALID_INPUT_EMAIL

    if db.session.query(User).filter(User.email == email).first():
        return API_STATUS.ERROR_PRIMARY

    if username == None or username == '':
        username = email.split('@')[0]

    if role == '' or role not in [ROLE.ADMIN, ROLE.GUEST, ROLE.USER]:
        return API_STATUS.ERROR_INVALID_INPUT

    status = USER_STATUS.OK
    password = generate_password_hash(BaseConfig.DEFAUTL_PASSWORD)
    login_failed = 0
    api_key = random_string(32)
    created_time = login_time = failed_time = get_time()

    user = User(email=email, username=username, password=password, status=status, mark=mark, role=role, api_key=api_key,
                login_failed=login_failed, created_time=created_time, login_time=login_time, failed_time=failed_time, description=description)

    if save_sql(user):
        return {'user': {'res': [email]}}
    else:
        return API_STATUS.ERROR

@mod.route('/edit', methods=['POST', 'GET'])
@login_check
@fix_response
def user_edit():
    id = int(request.json.get('id', ''))
    # email = request.json.get('email', '')
    # username = request.json.get('username', '')
    mark = request.json.get('mark', '')
    role = request.json.get('role', '')
    description = request.json.get('description', '')
    status = request.json.get('status', '')
    user = db.session.query(User).filter_by(id=id).first()
    if user:
        # if regex_deal(email, INPUT_TYPE.EMAIL):
        #     user.email = email
        #     user.username = email.split('@')[0]
        # else:
        #     return API_STATUS.ERROR_INVALID_INPUT_EMAIL

        # if db.session.query(User).filter(and_(User.email == email, User.id != user.id)).first():
        #     return API_STATUS.ERROR_PRIMARY

        if status in [USER_STATUS.OK, USER_STATUS.BAN]:
            user.status = status
        else:
            return API_STATUS.ERROR_INVALID_INPUT

        if role != '' and role in [ROLE.ADMIN, ROLE.GUEST, ROLE.USER]:
            user.role = role
        else:
            return API_STATUS.ERROR_INVALID_INPUT

        user.update_time = get_time()
        user.mark = mark
        user.description = description
        if save_sql(user):
            return {'user': {'res': [user.id]}}
        else:
            return API_STATUS.ERROR

    return API_STATUS.ERROR_IS_NOT_EXIST

@mod.route('/reset', methods=['POST', 'GET'])
@login_check
@fix_response
def user_reset():
    id = int(request.json.get('id', ''))
    user = db.session.query(User).filter_by(id=id).first()
    if user:
        user.api_key = random_string(32)
        user.password = generate_password_hash(BaseConfig.DEFAUTL_PASSWORD)
        user.update_time = get_time()
        if save_sql(user):
            return {'user': {'res': [user.id]}}
        else:
            return API_STATUS.ERROR

    return API_STATUS.ERROR_IS_NOT_EXIST