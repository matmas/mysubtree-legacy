from logging.handlers import SMTPHandler
from datetime import datetime, timedelta
from logging import LogRecord, CRITICAL
from lib.time import utcnow


class CarefulSMTPHandler(SMTPHandler):
    def __init__(self, *args, **kwargs):
        SMTPHandler.__init__(self, *args, **kwargs)
        self.last_emitted = datetime.min
        self.sent_flood_notice = False
    
    def emit(self, record):
        now = utcnow()
        if self.last_emitted + timedelta(minutes=60) < now:
            SMTPHandler.emit(self, record)
            self.last_emitted = now
            self.sent_flood_notice = False
        elif not self.sent_flood_notice:
            record = LogRecord(name="flood", level=CRITICAL, pathname="", lineno=0, msg="Flood", args=(), exc_info=None)
            SMTPHandler.emit(self, record)
            self.sent_flood_notice = True
