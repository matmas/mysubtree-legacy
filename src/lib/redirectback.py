from urlparse import urlparse, urljoin
from flask import request, redirect
from flask_wtf import Form, HiddenField
from mysubtree.web.app import app

def set_trusted_netloc(netloc):
    g.trusted_netloc = netloc

def _is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           test_url.netloc in (ref_url.netloc, app.config.get("TRUSTED_REFERER_NETLOC"))


def get_back_url():
    for target in request.values.get('next'), request.referrer:
        if target and _is_safe_url(target):
            return target

class RedirectForm(Form):
    next = HiddenField()
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_back_url() or ''

def redirect_back(target):
    back_url = get_back_url()
    if back_url and request.url != back_url: # prevent redirect to the same url over and over
        return redirect(back_url)
    return redirect(target)


def will_redirect_to_route(app, route):
    url = urlparse(get_back_url())
    url_route, params = app.url_map.bind("").match(url.path)
    return url_route == route