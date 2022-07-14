#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from flask import request
from flask import render_template
from flask import Blueprint
from flask import session
from sqlalchemy import and_
from lib.core.env import *
from lib.hander import db
from lib.core.model import DNSSetting
from lib.core.enums import ApiStatus
from lib.core.enums import DNSRedirect
from lib.util.util import get_time
from lib.hander.basehander import save_sql
from lib.hander.basehander import fix_response
from lib.hander.basehander import login_check

mod = Blueprint('dns', __name__, url_prefix=f'{PREFIX_URL}/dns')

@mod.route('/index', methods=['POST', 'GET'])
@login_check
def index():
    ctx = {}
    ctx['title'] = 'DNS'
    ctx['username'] = session.get('username')
    ctx['DNS_REDIRECT'] = DNSRedirect
    return render_template('manager/setting/dns.html', **ctx)

@mod.route('/list', methods=['POST', 'GET'])
@login_check
@fix_response
def list():
    response = {
        'data': {
            'res': [],
            'total': 0,
        }
    }
    page = request.json.get('page', 1)
    per_page = request.json.get('per_page', 10)
    name = request.json.get('name', '')
    domain = request.json.get('domain', '')
    value1 = request.json.get('value1', '')
    value2 = request.json.get('value2', '')
    dns_redirect = request.json.get('dns_redirect', '')

    condition = (1 == 1)
    if name != '':
        condition = and_(condition, DNSSetting.name.like('%' + name + '%'))

    if domain != '':
        condition = and_(condition, DNSSetting.domain.like('%' + domain + '%'))

    if value1 != '':
        condition = and_(condition, DNSSetting.value1.like('%' + value1 + '%'))

    if value2 != '':
        condition = and_(condition, DNSSetting.value2.like('%' + value2 + '%'))

    if dns_redirect != '' and isinstance(dns_redirect, bool):
        condition = and_(condition, DNSSetting.dns_redirect == dns_redirect)

    if per_page == 'all':
        for row in db.session.query(DNSSetting).filter(condition).order_by(DNSSetting.update_time.desc()).all():
            response['data']['res'].append(row.to_json())
    else:
        for row in db.session.query(DNSSetting).filter(condition).order_by(DNSSetting.update_time.desc()).paginate(page=page, per_page=per_page).items:
            response['data']['res'].append(row.to_json())
    response['data']['total'] = db.session.query(DNSSetting).filter(condition).count()
    return response


@mod.route('/edit', methods=['POST', 'GET'])
@login_check
@fix_response
def edit():
    dns_id = request.json.get('id', '')
    name = request.json.get('name', '')
    domain = request.json.get('domain', '')
    value1 = request.json.get('value1', '')
    value2 = request.json.get('value2', '')
    dns_redirect = request.json.get('dns_redirect', '')
    mark = request.json.get('mark', '')

    if dns_redirect != '' and isinstance(dns_redirect, bool) and dns_redirect and value2 == "":
        return ApiStatus.ERROR_INVALID_INPUT

    if dns_id != '':
        dns_id = int(dns_id)
        dns_setting = db.session.query(DNSSetting).filter(DNSSetting.id == dns_id).first()
        if dns_setting:
            dns_setting.mark = mark
            dns_setting.domain = domain
            dns_setting.value1 = value1
            dns_setting.value2 = value2
            dns_setting.dns_redirect = dns_redirect
            dns_setting.name = name
            dns_setting.update_time = get_time()
            save_sql(dns_setting)
            return {'data': {'res': [dns_id]}}
    return ApiStatus.ERROR_IS_NOT_EXIST


@mod.route('/add', methods=['POST', 'GET'])
@login_check
@fix_response
def add():
    name = request.json.get('name', '')
    domain = request.json.get('domain', '')
    value1 = request.json.get('value1', '')
    value2 = request.json.get('value2', '')
    dns_redirect = request.json.get('dns_redirect', False)
    mark = request.json.get('mark', '')

    if name == '':
        return ApiStatus.ERROR_INVALID_INPUT

    if value1 == '':
        return ApiStatus.ERROR_INVALID_INPUT

    if domain == '':
        return ApiStatus.ERROR_INVALID_INPUT

    if isinstance(dns_redirect, bool) and dns_redirect and value2 == "":
        return ApiStatus.ERROR_INVALID_INPUT

    update_time = get_time()

    dns_setting = DNSSetting(name=name, domain=domain, value1=value1, mark=mark,  value2=value2, dns_redirect=dns_redirect,
                                       update_time=update_time)
    save_sql(dns_setting)
    return {'data': {'res': [name]}}

@mod.route('/delete', methods=['POST', 'GET'])
@login_check
@fix_response
def delete():
    response = {'data': {'res': []}}
    dns_id = request.json.get('id', '')
    dns_ids = request.json.get('ids', '')
    if dns_id != '' or dns_ids != '':
        if dns_id != '':
            response = db.session.query(DNSSetting).filter(DNSSetting.id == dns_id).first()
            if response:
                db.session.delete(response)
                db.session.commit()
                response['data']['res'].append(dns_id)
        elif dns_ids != '':
            try:
                for dns_id in dns_ids.split(','):
                    dns_id = dns_id.replace(' ', '')
                    response = db.session.query(DNSSetting).filter(DNSSetting.id == dns_id).first()
                    if response:
                        db.session.delete(response)
                        db.session.commit()
                        response['data']['res'].append(dns_id)
            except:
                pass
        return response
    return ApiStatus.ERROR_IS_NOT_EXIST
