#autoimport
from flask import request, flash, redirect, jsonify, g
from flask.ext.babel import gettext as _
from flask_wtf import Form
from lib.redirectback import RedirectForm, redirect_back
from lib.error import Error
from lib.forms.keepempty import KeepEmpty
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.db import db
from mysubtree.web.babel import set_locale
from mysubtree.backend import backend
from mysubtree.web.user import get_user_node

@app.route("/delete/<nid>", methods=["GET", "POST"])
def delete(nid):
    node = backend.get_node_from(nid)
    set_locale(node.lang)
    class ActionForm(RedirectForm):
        keepempty = KeepEmpty()
    form = ActionForm()
    if request.method == "GET":
        title = "%s %s?" % (_("delete").capitalize(), node.short_name())
        return render_template("int/routes/node/action.html", action="delete", action_name=_("delete"), title=title, node=node, form=form, lang=node.lang, btn_class="btn-danger")
    else: # POST
        try:
            if not form.validate():
                raise Error(_("Form did not have all fields filled correctly."))
            node.delete()
            db.session.commit()
            if request.is_xhr: # AJAX
                return jsonify({
                    "refresh_siblings": {"nid": node.nid()},
                    "refresh_ancestors": {"nid": node.nid()}, # because of consistent activity
                })
            flash(_("Deleted successfully."), category="info")
            return redirect_back(node.url())
        except Error as error:
            if request.is_xhr: # AJAX
                return jsonify(error=unicode(error))
            else:
                flash(unicode(error), category="error")
                return redirect_back(node.url())
