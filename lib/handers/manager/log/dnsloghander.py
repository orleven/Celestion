#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

from flask import request
from flask import render_template
from flask import Blueprint
from flask import session
from sqlalchemy import and_
from lib.handers import db
from lib.core.model import DNSLog
from lib.core.enums import API_STATUS
from lib.utils.util import get_time
from lib.utils.util import get_timestamp
from lib.handers.basehander import fix_response
from lib.handers.basehander import login_check

mod = Blueprint('dnslog', __name__, url_prefix='/dnslog')

@mod.route('/index', methods=['POST', 'GET'])
@login_check
def dnslog_index():
    ctx = {}
    ctx['title'] = 'DNSLog'
    ctx['username'] = session.get('username')
    return render_template('manager/log/dnslog.html', **ctx)

@mod.route('/list', methods=['POST', 'GET'])
@login_check
@fix_response
def dnslog_list():
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
    dns_domain = request.json.get('dns_domain', '')
    dnslog_type = request.json.get('type', '')
    condition = (1 == 1)

    if domain != '':
        condition = and_(condition, DNSLog.domain.like('%' + domain + '%'))

    if ip != '':
        condition = and_(condition, DNSLog.ip.like('%' + ip + '%'))

    if dns_domain != '':
        condition = and_(condition, DNSLog.dns_domain.like('%' + dns_domain + '%'))

    if dnslog_type != '':
        condition = and_(condition, DNSLog.type.like('%' + dnslog_type + '%'))

    if per_page == 'all':
        for row in db.session.query(DNSLog).filter(condition).order_by(DNSLog.update_time.desc()).all():
            response['data']['res'].append(row.to_json())
    else:
        for row in db.session.query(DNSLog).filter(condition).order_by(DNSLog.update_time.desc()).paginate(page=page, per_page=per_page).items:
            response['data']['res'].append(row.to_json())
    response['data']['total'] = db.session.query(DNSLog).filter(condition).count()
    return response


@mod.route('/delete', methods=['POST', 'GET'])
@login_check
@fix_response
def dnslog_delete():
    response = {'data': {'res': []}}
    dnslog_id = request.json.get('id', '')
    dnslog_ids = request.json.get('ids', '')
    if dnslog_id != '' or dnslog_ids != '':
        if dnslog_id != '':
            dnslog = db.session.query(DNSLog).filter(DNSLog.id == dnslog_id).first()
            if dnslog:
                db.session.delete(dnslog)
                db.session.commit()
                response['data']['res'].append(dnslog_id)
        elif dnslog_ids != '':
            try:
                for dnslog_id in dnslog_ids.split(','):
                    dnslog_id = dnslog_id.replace(' ', '')
                    dnslog = db.session.query(DNSLog).filter(DNSLog.id == dnslog_id).first()
                    if dnslog:
                        db.session.delete(dnslog)
                        db.session.commit()
                        response['data']['res'].append(dnslog_id)
            except:
                pass
        return response
    return API_STATUS.ERROR_IS_NOT_EXIST


@mod.route('/clear_old', methods=['POST', 'GET'])
@login_check
@fix_response
def dnslog_clear_old():
    response = {'data': {'res': []}}
    delete_time = get_time(get_timestamp() - 60 * 60 * 24 * 1)
    condition = (1 == 1)
    condition = and_(condition, DNSLog.update_time <= delete_time)
    db.session.query(DNSLog).filter(condition).delete(synchronize_session=False)
    return response
