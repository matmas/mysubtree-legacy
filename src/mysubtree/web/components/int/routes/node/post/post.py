#autoimport
from datetime import datetime
from flask import request, flash, redirect, jsonify, json, make_response, g, abort
from flask_wtf import Form
from flaskext.babel import gettext as _
from lib import utils
from lib.error import Error
from lib.wtforms.keepempty import KeepEmpty
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.backend import backend, common
from mysubtree.db import db
from mysubtree.web.babel import set_locale
from mysubtree.backend.models.node.types.all import get_model
from mysubtree.web.components.int.routes.middleware.ajax_response import ajax_response
from mysubtree.web.components.int.routes.middleware.refresh_account import refresh_account

@app.route("/post/<type>/to/<nparent>-<nid>", methods=["GET", "POST"])
@app.route("/post/<type>/to/<nid>",           methods=["GET", "POST"])
@app.route("/post-to/<nparent>-<nid>",        methods=["GET", "POST"])
@app.route("/post-to/<nid>",                  methods=["GET", "POST"])
@ajax_response
@refresh_account
def post(nid, type=None, nparent=None, slug=None):
    app.jinja_env.globals.update(locals())
    node = backend.get_node_from(nid, nparent) or abort(404)
    set_locale(node.lang)
    if request.method == "GET":
        if type:
            types = [type]
        else:
            types = node.types_in_menu()
        forms = {}
        for type in types:
            form = _get_form(node, type)
        
            # prefill form default values:
            for field, default_velue in get_model(type).get_form_default_values(parent_node=node):
                form[field].data = default_velue
            
            forms[type] = form
        
        #if len(forms) == 1:
            #forms[0].  widget=TextInput(autofocus=True)
        
        return render_template("post.html", node=node, lang=node.lang, types=types, forms=forms)
    else: #POST
        if not type:
            abort(403)
        form = _get_form(node, type)
        try:
            if not form.validate():
                raise Error(_("Form did not have all fields filled correctly."))
            newnode = get_model(type)()
            form.populate_obj(newnode)
            delattr(newnode, "keepempty")
            newnode.set_parent(node)
            newnode.add()
            db.session.commit()
            if g.is_ajax:
                return {
                    "refresh": { "nid": node.nid(),
                        "refresh_nodes": {"nid": node.nid()},
                        "refresh_ancestors": {"nid": node.nid()},
                    },
                }
            flash(_("Posted successfully."), category="info")
            return redirect(node.url(type=type)) # new node must be visible to prevent confusion
        except Error as error:
            if g.is_ajax:
                return {
                    "error": unicode(error),
                    "html": render_template("post.html", node=node, lang=node.lang, types=[type], forms={type: form}),
                }
            flash(unicode(error), category="error")
            return render_template("post.html", node=node, lang=node.lang, types=[type], forms={type: form})

                
def _get_form(node, type):
    class DynamicForm(Form):
        keepempty = KeepEmpty()
    for field_name, field in get_model(type).get_form_fields(parent_node=node):
        setattr(DynamicForm, field_name, field)
    return DynamicForm(request.form)



