#autoimport
from flask import request, flash, redirect, jsonify, g, abort, url_for
from flaskext.babel import gettext as _
from flask_wtf import Form, fields, validators
from lib.wtforms.widgets import TextInput
from lib.redirectback import RedirectForm, redirect_back
from lib.error import Error
from lib.wtforms.keepempty import KeepEmpty
from mysubtree.web.app import app
from mysubtree.db import db
from mysubtree.web.templating import render_template
from mysubtree.web.babel import set_locale
from mysubtree.backend import backend

@app.route("/rename/<nid>", methods=["GET", "POST"])
def rename(nid):
    node = backend.get_node_from(nid)
    set_locale(node.lang)
    class RenameForm(RedirectForm):
        name = fields.TextField("", [
            validators.Required(message=_("This field is required.")),
        ], widget=TextInput(autofocus=True))
        keepempty = KeepEmpty()
    form = RenameForm()
    if not node.is_renameable():
        abort(403)
    if request.method == "GET":
        form["name"].data = node.name # prefill form default value:
        return render_template("int/routes/node/action.html", action="rename", action_name=_("rename"), node=node, lang=node.lang, form=form)
    else: # POST
        try:
            if not form.validate():
                raise Error(_("Form did not have all fields filled correctly."))
            if node.rename(form.name.data):
                db.session.commit()
                if request.is_xhr: # AJAX
                    return jsonify({"refresh": {"nid": node.nid(), "highlight": True}})
                flash(_("Renamed successfully."), category="info")
            else:
                if request.is_xhr: # AJAX
                    return jsonify({"refresh": {"nid": node.nid()}})
            return redirect_back(node.url())
        except Error as error:
            if request.is_xhr: # AJAX
                return jsonify(error=unicode(error))
            else:
                flash(unicode(error), category="error")
                return redirect_back(node.url())
