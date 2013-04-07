#autoimport
from flask import request, g, flash, redirect, jsonify, Markup, url_for, abort
from flask_wtf import Form, fields, validators
from flaskext.babel import gettext as _
from lib.wtforms.widgets import TextArea
from lib.redirectback import RedirectForm, redirect_back
from lib.wtforms import widgets
from lib.wtforms.keepempty import KeepEmpty
from lib.error import Error
from mysubtree.backend import backend
from mysubtree.backend.models.node.types.all import get_model
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.db import db
from mysubtree.web.babel import set_locale
from mysubtree.web.user import get_user_node

@app.route("/edit/<nid>", methods=["GET", "POST"])
def edit(nid):
    node = backend.get_node_from(nid)
    set_locale(node.lang)
    class EditForm(RedirectForm):
        #body = fields.TextAreaField("", widget=widgets.WikiareaWidget(
            #preview_position="top" if g.is_ajax else "bottom",
            #top_html = Markup("<div class='clear-body'></div>") if node.type == "items" else "",
        #))
        body = fields.TextAreaField("", widget=TextArea(autofocus=True))
        version = fields.HiddenField()
        keepempty = KeepEmpty()
    form = EditForm()
    if not node.is_editable():
        abort(403)
    can_edit_directly = (get_user_node() in node.get_moderators() and node.type != "edit-suggestions")

    if request.method == "GET":
        # prefill default values:
        form["body"].data = node.body 
        form["version"].data = node.version + 1
        if can_edit_directly:
            action_name = _("save")
            title = "%s %s" % (_("edit").capitalize(), node.short_name())
        else:
            action_name = _("suggest edit")
            title = None # default
        return render_template("int/routes/node/action.html", action="edit", action_name=action_name, title=title, node=node, form=form, lang=node.lang)
    else: # POST
        try:
            if not form.validate():
                raise Error(_("Form did not have all fields filled correctly."))
            if can_edit_directly:
                if node.edit(new_body=form.body.data, new_version=int(form.version.data)):
                    db.session.commit()
                    if request.is_xhr: # AJAX
                        return jsonify({"refresh": {"nid": node.nid(), "highlight": True}, "refresh_nodes": {"nid": node.nid()}, "refresh_ancestors": {"nid": node.nid()}}) # refresh_ancestors because of consistent activity
                    flash(_("Saved successfully."), category="info")
                else:
                    if request.is_xhr: # AJAX
                        return jsonify({"refresh": {"nid": node.nid()}})
            else:
                newnode = get_model("edit-suggestions")()
                form.populate_obj(newnode)
                delattr(newnode, "keepempty")
                newnode.set_parent(node)
                newnode.add()
                db.session.commit()
                ajax_response = {
                    "refresh": { "nid": node.nid(),
                        "refresh_nodes": {"nid": node.nid()},
                        "refresh_ancestors": {"nid": node.nid()},
                    },
                }
                if request.is_xhr: # AJAX
                    return jsonify(ajax_response)
                flash(_("Posted successfully."), category="info")
            return redirect_back(node.url())
        except Error as error:
            if request.is_xhr: # AJAX
                return jsonify(error=unicode(error))
            else:
                flash(unicode(error), category="error")
                return redirect_back(node.url())
