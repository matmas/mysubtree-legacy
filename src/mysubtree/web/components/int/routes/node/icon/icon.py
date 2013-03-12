#autoimport
from base64 import b64encode
import magic
from flask import request, flash, redirect, jsonify, make_response, g, abort
from flaskext.babel import gettext as _
from flask_wtf import Form, fields, validators
from lib.json import json
from lib.redirectback import RedirectForm, redirect_back
from lib.wtforms.validators import FileRequired, ImageSize, FileExtension
from lib.error import Error
from lib.wtforms.keepempty import KeepEmpty
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.backend import backend
from mysubtree.db import db
from mysubtree.web.babel import set_locale
from mysubtree.web.user import get_user_node

class MimeType:
    def __init__(self, mimetype):
        self.mimetype = mimetype
    def __call__(self, form, field):
        if request.files[field.name].filename != "":
            stream = request.files[field.name].stream
            stream.seek(0)
            buffer = stream.read()
            detected_mime = magic.from_buffer(buffer, mime=True)
            if detected_mime != self.mimetype:
                raise validators.StopValidation(_("Mime-type %(m1)s is not allowed. Allowed mime-type is %(m2)s.", m1=detected_mime, m2=self.mimetype))
            request.files[field.name].detected_mime = detected_mime

@app.route("/icon/<nparent>-<nid>", methods=["GET", "POST"])
def icon(nparent, nid):
    node = backend.get_node_from(nid, nparent)
    set_locale(node.lang)
    class IconForm(RedirectForm):
        use = fields.SelectField(_("Use"),
            choices=[("default", _("default icon")), ("custom", _("custom icon"))],
            default="custom",
        )
        icon = fields.FileField('PNG 16x16', [
            FileExtension("png"),
            MimeType("image/png"),
            ImageSize(16, 16),
        ])
        def validate_icon(form, field):
            if form.use.data == "custom" and not request.files[field.name]:
                raise validators.StopValidation(message=_("This field is required."))
        keepempty = KeepEmpty()
    form = IconForm()
    if not node.is_icon_changeable():
        abort(403)
    if request.method == "GET":
        return render_template("int/routes/node/action.html", action="icon", action_name=_("set icon"), node=node, lang=node.lang, form=form)
    else: # POST
        try:
            if not form.validate():
                raise Error(_("Form did not have all fields filled correctly."))
            if form.use.data == "custom":
                file = request.files["icon"]
                stream = file.stream
                stream.seek(0)
                buffer = stream.read()
                icon = "data:%s;base64,%s" % (file.detected_mime, b64encode(buffer))
            else:
                icon = None
            
            if node.set_icon(icon):
                db.session.commit()
                ajax_response = {"refresh": {"nid": node.nid(), "highlight": True}}
                if g.is_iframe:
                    return make_response('<textarea data-type="application/json">%s</textarea>' % json.dumps(ajax_response))
                elif request.is_xhr: # AJAX
                    return jsonify(ajax_response)
                flash(_("Set icon successfully."), category="info")
            else:
                ajax_response = {"refresh": {"nid": node.nid()}}
                if g.is_iframe:
                    return make_response('<textarea data-type="application/json">%s</textarea>' % json.dumps(ajax_response))
                elif request.is_xhr: # AJAX
                    return jsonify(ajax_response)
            return redirect_back(node.url())
        except Error as error:
            html = render_template("int/routes/node/action.html", action="icon", action_name=_("set icon"), node=node, lang=node.lang, form=form)
            if g.is_iframe:
                return make_response('<textarea data-type="application/json">%s</textarea>' % json.dumps({
                    "error": unicode(error), "html": html,
                }))
            elif request.is_xhr: # AJAX
                return jsonify(error=unicode(error), html=html)
            else:
                flash(unicode(error), category="error")
                return html
