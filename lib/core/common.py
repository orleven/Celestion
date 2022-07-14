#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import json
import requests
from lib.core.g import conf

def seng_message(msg="", reminders=None):

    if reminders is None:
        reminders = []

    url = conf.basic.dingding_robot_url
    timeout = conf.basic.timeout
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "msgtype": "text",
        "at": {
            "atMobiles": reminders,
            "isAtAll": False,
        },
        "text": {
            "content": msg,
        }
    }
    error = ""
    for i in range(0, 3):
        try:
            r = requests.post(url, data=json.dumps(data), headers=headers, timeout=timeout)
            return True, r.text
        except Exception as e:
            error = get_safe_ex_string(e)
    return False, error

