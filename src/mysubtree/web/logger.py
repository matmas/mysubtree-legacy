import logging
from flask import request

class VisitorLoggingFilter(logging.Filter):
    def filter(self, record):
        record.remote_addr = request.remote_addr
        record.user_agent = request.user_agent.string
        record.referrer = request.referrer
        record.accept_languages = request.accept_languages
        record.session = request.cookies.get("session", "")
        return True

import sys
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('"%(asctime)s";"%(remote_addr)s";"%(message)s";"%(user_agent)s";"%(accept_languages)s";"%(referrer)s";%(session)s'))
handler.addFilter(VisitorLoggingFilter())
logging.getLogger("web").addHandler(handler)

#IP: %(ip)-15s User: %(user)-8s 

#def get_info():
    #return '%(remote_addr)s;"%(user_agent)s";"%(referrer)s";"%(accept_languages)s";%(session)s' % {
        #"remote_addr": 
        
    #}

#makeRecord = logger.makeRecord
#def makeBetterRecord(name, lvl, fn, lno, msg, args, exc_info, *vargs, **kwargs):
    #msg = msg + 
    #print dir(request)
    #return makeRecord(name, lvl, fn, lno, msg, args, exc_info, *vargs, **kwargs)
#logger.makeRecord = makeBetterRecord

