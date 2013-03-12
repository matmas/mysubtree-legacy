#autoimport
from flask import request, flash, redirect, g, jsonify, abort, url_for
from flaskext.babel import gettext as _
from flask_wtf import Form
from lib.redirectback import RedirectForm, redirect_back
from lib.base57 import base_encode
from lib.error import Error
from mysubtree.backend import backend
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.db import db
from mysubtree.web.babel import set_locale

@app.route("/accept/<nparent>-<nid>", methods=["GET", "POST"])
def accept(nparent, nid):
    node = backend.get_node_from(nid, nparent)
    set_locale(node.lang)
    form = RedirectForm()
    if request.method == "GET":
        title = "%s %s?" % (_("accept").capitalize(), node.short_name())
        return render_template("int/routes/node/action.html", action="accept", action_name=_("accept"), title=title, node=node, form=form)
    else: # POST
        try:
            parent_node_url = url_for("node", lang=node.lang, nid=node.nparent(), nparent=base_encode(node.parent_of_parent), slug=node.path[-1]["slug"])
            if not form.validate():
                raise Error(_("Form did not have all fields filled correctly."))
            node.accept()
            db.session.commit()
            if request.is_xhr: # AJAX
                return jsonify({
                    "refresh": {"nid": nparent, "highlight": True,
                        "refresh_nodes": {"nid": nparent}
                    },
                    "refresh_ancestors": {"nid": nparent} # because of consistent activity
                })
            flash(_("Accepted sucessfully."), category="info")
            return redirect_back(parent_node_url)
        except Error as error:
            if request.is_xhr: # AJAX
                return jsonify(error=unicode(error))
            else:
                flash(unicode(error), category="error")
                return redirect_back(parent_node_url)
