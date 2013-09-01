from datetime import datetime, timedelta
from flask.ext.babel import gettext as _, ngettext
from lib.time import utcnow
from lib.error import Error

_request_times = {}
_request_counts = {}

def limit(what, num_requests=1, num_seconds=60):
    """Raises Error when called more than num_requests times in num_seconds seconds.
    what -- typically IP address
    """
    _cleanup()
    if _request_times.get(what, datetime.min) + timedelta(seconds=num_seconds) > utcnow():
        if _request_counts[what] >= num_requests:
            n_requests = ngettext("%(num)s request", "%(num)s requests", num=num_requests)
            n_seconds = ngettext("%(num)s second", "%(num)s seconds", num=num_seconds)
            raise Error(_("At most %(n_requests)s in %(n_seconds)s is allowed.", n_requests=n_requests, n_seconds=n_seconds))
        else:
            _request_counts[what] += 1
    else:
        _request_times[what] = utcnow()
        _request_counts[what] = 1

def _cleanup():
    for what, time in _request_times.items():
        print time, time + timedelta(hours=24) < utcnow()
        if time + timedelta(seconds=1) < utcnow():
            del _request_times[what]
            del _request_counts[what]
 