#autoimport
# -*- coding: utf-8 -*-
from flask.ext.babel import gettext as _, ngettext
from lib.time import utcnow
from mysubtree.web.app import app

@app.template_filter()
def timesince(dt, default=None, coarse=False, prefix=""):
    """
    Returns string representing "time since" e.g.
    3 days ago, 5 hours ago etc.
    """
    if not default:
        default = _("just now")
    if dt is None:
        return ""
    now = utcnow()
    diff = now - dt
    
    num = diff.days / 365
    if num:
        return prefix + ngettext("%(num)s year ago", "%(num)s years ago", num)
    num = diff.days / 30
    if num:
        return prefix + ngettext("%(num)s month ago", "%(num)s months ago", num)
    num = diff.days / 7
    if num:
        return prefix + ngettext("%(num)s week ago", "%(num)s weeks ago", num)
    num = diff.days
    if num:
        return prefix + ngettext("%(num)s day ago", "%(num)s days ago", num)
    num = diff.seconds / 3600
    if num:
        return prefix + ngettext("%(num)s hour ago", "%(num)s hours ago", num)
    num = diff.seconds / 60
    if num:
        return prefix + ngettext("%(num)s minute ago", "%(num)s minutes ago", num)
    if not coarse:
        num = diff.seconds
        if num:
            return prefix + ngettext("%(num)s second ago", "%(num)s seconds ago", num)
    if coarse:
        default = _("less than a minute ago")
    return prefix + default


#@app.template_filter("max")
#def max_filter(*values):
    #return max(*values)

#@app.template_filter("sorted")
#def sorted_filter(iterable, attribute=None, **params):
    #if attribute:
        #from operator import itemgetter
        #return sorted(iterable, key=itemgetter(attribute), **params)
    #else:
        #return sorted(iterable)

#@app.template_filter("limit_to")
#def limit_to_filter(iterable, num):
    #return iterable[:num]

@app.template_filter()
def activity_level(dt):
    if dt is None:
        return ""
    now = utcnow()
    diff = now - dt
    periods = (
        (diff.days / 365 * 2, "years"), # years
        (diff.days / 30 * 2, "months"), # months
        (diff.days / 7 * 2, "weeks"), # weeks
        (diff.days * 2, "days"), # days
        (diff.seconds / 3600 * 2, "hours"), # hours
        (diff.seconds / 60 * 2, "minutes"), # minutes
    )
    for period, level in periods:
        if period:
            return level
    return periods[-1][-1] # now

@app.template_filter("__")
def content_gettext(input):
    """
    >>> translate("root")
    'root'
    >>> translate("_(root)")
    'koreň'
    """
    if input.startswith("_(") and input.endswith(")"):
        inner = input[2:-1]
        return _(inner)
    return input

