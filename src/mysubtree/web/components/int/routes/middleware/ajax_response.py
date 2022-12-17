from flask import request, g, jsonify, make_response, json
from mysubtree.web.app import app


@app.before_request
def before_request():
    g.is_iframe = request.form.get("X-Requested-With") == "IFrame"
    g.is_ajax = request.is_xhr or g.is_iframe


def ajax_response(route):
    def wrapper(**kwargs):
        response = route(**kwargs)
        if isinstance(response, dict):
            if request.is_xhr: # AJAX
                return jsonify(response)
            elif g.is_iframe:
                return make_response('<textarea data-type="application/json">%s</textarea>' % json.dumps(response))
            else:
                assert False
        return response # HTML
    wrapper.__name__ = route.__name__ # for url_for to work
    return wrapper
    