#autoimport
import urllib2
from urlparse import urlparse
from flask import request, redirect, url_for, flash, abort, session, jsonify
from flaskext.babel import gettext as _
from flask_wtf import Form, fields
from lib.redirectback import RedirectForm, redirect_back
from lib.base57 import base_decode
from lib.error import Error
from mysubtree.backend import backend
from mysubtree.web.app import app
from mysubtree.db import db
from mysubtree.web.templating import render_template
from mysubtree.backend.models.node.node import Node
from mysubtree.web.user import get_user_node
from mysubtree.web.babel import set_locale

def cancel_moving():
    if "moving_node" in session:
        del session["moving_node"]

@app.route("/move-to/<nparent>-<nid>", methods=["GET", "POST"])
@app.route("/move-to/<nid>",           methods=["GET", "POST"]) # root
def move_to(nid, nparent=None, moving_node_nid=None):
    
    moving_node_info = session.get("moving_node") or {}
    
    moving_node_nid = moving_node_info.get("nid")
    moving_node_nparent = moving_node_info.get("nparent")
    node = backend.get_node_from(nid, nparent)
    
    if not moving_node_nid:
        return redirect_back(node.url())
    
    if request.args.get("moving_node_url"):
        try:
            moving_node_url = request.args.get("moving_node_url")
            url = urlparse(moving_node_url)
            route, params = app.url_map.bind("").match(url.path)
            route == "node" or abort(403)
            moving_node_nid = params.get("nid")
            moving_node_nparent = params.get("nparent")
        except AttributeError:
            abort(403)
    
    moving_node = backend.get_node_from(moving_node_nid, moving_node_nparent)
    
    set_locale(node.lang)
    form = RedirectForm()
    if request.method == "GET":
        
        warning = None
        if get_user_node() != moving_node.user and get_user_node() not in node.get_moderators():
            warning = _('Are you sure? You would cease to be moderator of that node if you move it there. That means also that you would not be able to move it back yourself.')
        
        if request.is_xhr: # AJAX
            return jsonify({"warning": warning})
        if warning:
            flash(warning, category="info")
        return render_template("move_to.html", node=node, lang=node.lang, form=form)
    else: # POST
        try:
            if not form.validate():
                raise Error(_("Form did not have all fields filled correctly."))
            
            if not request.args.get("cancel"):
                old_parent_nid = moving_node.nparent()
                if moving_node.move(node):
                    db.session.commit()
                    if request.is_xhr: # AJAX
                        return jsonify({
                            "refresh_nodes": { "nid": old_parent_nid,
                                "refresh": { "nid": old_parent_nid,
                                    "refresh": { "nid": nid,
                                        "refresh_nodes": { "nid": nid },
                                    }
                                }
                            }
                        })
                    flash(_("Moved successfully."), category="info")
                cancel_moving()
                if request.is_xhr: # AJAX
                    return jsonify({})
                return redirect(moving_node.url())
            else:
                cancel_moving()
            return redirect_back(node.url())
        except Error as error:
            if request.is_xhr: # AJAX
                return jsonify(error=unicode(error))
            else:
                flash(unicode(error), category="error")
                return redirect_back(node.url())