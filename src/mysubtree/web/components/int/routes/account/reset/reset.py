#autoimport
from datetime import timedelta
from flask import request, redirect, flash, url_for, g
from flaskext.babel import gettext as _
from flask_wtf import Form, fields, validators
from lib.wtforms.widgets import TextInput
from lib.time import utcnow
from lib.error import Error
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.db import db
from mysubtree.backend.models.user import User
from mysubtree.web.babel import set_locale
from ..password_validators import get_password_validators

@app.route("/<lang>/reset/<code>", methods=["GET", "POST"])
def reset(lang, code):
    set_locale(lang)
    class ResetPasswordForm(Form):
        password = fields.PasswordField(_("New password"), get_password_validators(), widget=TextInput(autofocus=True))
        password_again = fields.PasswordField(_("Repeat password"), [
            validators.Required(message=_("This field is required.")),
            validators.EqualTo("password", message=_("Passwords must match")),
        ])
    form = ResetPasswordForm(csrf_enabled=False)
    
    user = User.query.filter_by(reset_code=code).first()
    if not user or user.reset_date + timedelta(hours=24) < utcnow():
        flash(_("Invalid reset code."), category="error")
        return redirect(url_for("forgot"))
    
    if request.method == "GET":
        return render_template("reset.html", form=form, code=code)
    else: # POST
        if g.is_ajax: # just for form validation
            field = form._fields.get(request.form.get("validate_field"))
            if field:
                field.validate(form)
                return render_template("int/errors/errors.html", field=field)
            return ""
        else:
            try:
                if not form.validate():
                    raise Error(_("Form did not have all fields filled correctly."))
                
                user.set_password(form.password.data)
                user.reset_code = None
                user.reset_date = None
                db.session.commit()
                flash(_("Password changed successfully."), category="info")
                return redirect(url_for("login", lang=lang))
            except Error as error:
                flash(unicode(error), category="error")
                return render_template("reset.html", form=form, code=code)
