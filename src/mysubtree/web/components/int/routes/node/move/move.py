#autoimport
from flask import request, flash, redirect, jsonify, session, abort
from flaskext.babel import gettext as _
from flask_wtf import Form
from lib.redirectback import RedirectForm, redirect_back
from lib.error import Error
from lib.base57 import base_decode
from lib.wtforms.keepempty import KeepEmpty
from mysubtree.backend import backend
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.db import db
from mysubtree.web.babel import set_locale

@app.route("/move/<nparent>-<nid>", methods=["GET", "POST"])
def move(nparent, nid):
    node = backend.get_node_from(nid, nparent) or abort(404)
    set_locale(node.lang)
    form = RedirectForm()
    if request.method == "GET":
        title = "%s %s" % (_("move").capitalize(), node.short_name())
        return render_template("int/routes/node/action.html", action="move", action_name=_("move this somewhere..."), title=title, node=node, form=form, lang=node.lang)
    else: # POST
        try:
            if not form.validate():
                raise Error(_("Form did not have all fields filled correctly."))
            
            session["moving_node"] = {
                "nid": node.nid(),
                "nparent": node.nparent(),
                "type": node.type,
            }
            
            if request.is_xhr: # AJAX
                return jsonify({})
            flash(_("You may now paste the node somewhere."), category="info")
            return redirect_back(node.url())
        except Error as error:
            if request.is_xhr: # AJAX
                return jsonify(error=unicode(error))
            else:
                flash(unicode(error), category="error")
                return redirect_back(node.url())
