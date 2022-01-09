#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: orleven

import time
import threading
from queue import Queue
from dnslib import RR
from dnslib import QTYPE
from dnslib import RCODE
from dnslib import TXT
from dnslib import A
from dnslib.server import DNSServer
from dnslib.server import BaseResolver
from sqlalchemy import and_
from lib.core.config import BaseConfig
from lib.core.data import log
from lib.core.data import cache_log
from lib.core.model import DNSLog
from lib.core.model import DNSSetting
from lib.handers import db
from lib.handers.basehander import save_sql
from lib.utils.util import get_time
from lib.utils.util import seng_message
from lib.utils.util import get_timestamp

class DNSServerLogger:

    def __init__(self, msg_queue):
        self.msg_queue = msg_queue
        self.dns_domain = BaseConfig.DNS_DOMAIN
        self.admin_domain = BaseConfig.ADMIN_DOMAIN

    def log_data(self, dnsobj):
        pass

    def log_error(self, handler, e):
        pass

    def log_pass(self, *args):
        pass

    def log_prefix(self, handler):
        pass

    def log_recv(self, handler, data):
        pass

    def log_reply(self, handler, reply):
        domain = reply.q.qname.__str__().lower()[:-1]
        ip = handler.client_address[0]
        update_time = get_time()
        dns_type = QTYPE[reply.q.qtype]
        if domain.endswith(self.dns_domain) and domain not in [self.admin_domain]:
            dnslog = DNSLog(ip=ip, dns_domain=self.dns_domain, domain=domain, type=dns_type, update_time=update_time)
            save_sql(dnslog)
            msg = f'Receice dns request, domain: {domain}, ip: {ip}, type: {dns_type}, time: {update_time}'
            cache_log.info(msg)

            msg = f'DNSLOG 上线\ndomain: {domain}\nip: {ip}\ntype: {dns_type}\ntime: {update_time}'
            self.msg_queue.put(msg)

    def log_request(self, handler, request):
        pass

    def log_send(self, handler, data):
        pass

    def log_truncated(self, handler, reply):
        pass


class DNSServerResolver(BaseResolver):
    """
        Simple fixed zone file resolver.
    """

    def __init__(self):
        """
            Initialise resolver from zone file.
            Stores RRs as a list of (label,type,rr) tuples
            If 'glob' is True use glob match against zone file
        """

        self.ns1_domain = BaseConfig.NS1_DOMAIN
        self.ns2_domain = BaseConfig.NS2_DOMAIN
        self.server_ip = BaseConfig.DEFAULT_SERVER_IP
        self.dns_domain = BaseConfig.DNS_DOMAIN
        self.admin_domain = BaseConfig.ADMIN_DOMAIN
        self.admin_server_ip = BaseConfig.ADMIN_SERVER_IP
        zone = f'''
*.{self.dns_domain}.       IN      NS      {self.ns1_domain}.
*.{self.dns_domain}.       IN      NS      {self.ns2_domain}.
*.{self.dns_domain}.       IN      A       {self.server_ip}
{self.dns_domain}.       IN      A       {self.server_ip}
'''
        self.zone = [(rr.rname, QTYPE[rr.rtype], rr) for rr in RR.fromZone(zone)]
        self.eq = 'matchGlob'

    def resolve(self, request, handler):
        """
            Respond to DNS request - parameters are request packet & handler.
            Method is expected to return DNS response
        """
        reply = request.reply()
        try:
            qname = request.q.qname
            qtype = QTYPE[request.q.qtype]
            domain = str(qname).rstrip('.')
            ip = handler.client_address[0]
            if qtype == 'TXT':
                reply.add_answer(RR(qname, QTYPE.TXT, ttl=0, rdata=TXT("")))

            for name, rtype, rr in self.zone:
                if getattr(qname, self.eq)(name) and (qtype == rtype or qtype == 'ANY' or rtype == 'CNAME'):

                    dns_setting = db.session.query(DNSSetting).filter(
                        and_(DNSSetting.domain == domain, DNSSetting.type == 'A')).order_by(
                        DNSSetting.update_time.desc()).first()

                    if dns_setting:
                        # DNS 重定向
                        if dns_setting.dns_redirect:
                            dns_log = db.session.query(DNSLog).filter(and_(DNSLog.domain == domain, DNSLog.ip == ip,
                                                                           DNSLog.update_time > get_time(
                                                                               get_timestamp() - 10))).first()

                            if dns_log:
                                answer = RR(qname, QTYPE.A, ttl=0, rdata=A(dns_setting.value2))
                            else:
                                answer = RR(qname, QTYPE.A, ttl=0, rdata=A(dns_setting.value1))
                        else:
                            answer = RR(qname, QTYPE.A, ttl=0, rdata=A(dns_setting.value1))
                    else:
                        answer = RR(qname, QTYPE.A, ttl=0, rdata=A(self.server_ip))
                    reply.add_answer(answer)

                if rtype in ['CNAME', 'NS', 'MX', 'PTR']:
                    for a_name, a_rtype, a_rr in self.zone:
                        if a_name == rr.rdata.label and a_rtype in ['A', 'AAAA']:
                            reply.add_ar(a_rr)
        except:
            pass
        finally:
            if not reply.rr:
                reply.header.rcode = RCODE.NXDOMAIN

        return reply

def dns_server(address='0.0.0.0', port=53):
    msg_queue = Queue()

    t = threading.Thread(target=msg_center, args=(msg_queue,))
    t.start()

    resolver = DNSServerResolver()
    log.info("Starting Zone Resolver (%s:%d) [%s]" % ("*", 53, "UDP"))
    udp_server = DNSServer(resolver, port=port, address=address, logger=DNSServerLogger(msg_queue))
    udp_server.start()

def msg_center(msg_queue):
    while True:
        if msg_queue.qsize() > 0:
            msg = msg_queue.get()
            flag, err = seng_message(msg)
            msg = msg.replace('\n', ', ').replace('\r', ', ')
            if flag:
                log.success(f'Send message to IM, msg: {msg}')
            else:
                log.error(f'Send message to IM error, msg: {msg}, error: {err}')
        time.sleep(0.1)

if __name__ == '__main__':
    dns_server()


