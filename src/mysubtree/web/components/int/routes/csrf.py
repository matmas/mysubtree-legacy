#autoimport
from flask import request, jsonify, abort
from flask_wtf import Form
from mysubtree.web.app import app

@app.route("/csrf")
def csrf():
    if request.is_xhr: # X-Requested-With
        class AForm(Form):
            pass
        form = AForm()
        csrf_token = form.csrf_token.current_token
        return jsonify(csrf_token=csrf_token)
    else:
        abort(403)
