#autoimport
import logging
from flask import request, flash, url_for, g, Markup, jsonify
from flask_wtf import fields, validators
from flaskext.babel import gettext as _
from lib.wtforms.widgets import TextInput
from lib.redirectback import RedirectForm, redirect_back
from lib.error import Error
from mysubtree.backend.models.user import User
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.web.user import set_user, get_user
from mysubtree.web.babel import set_locale

logger = logging.getLogger("web")

@app.route("/<lang>/login", methods=["GET", "POST"])
def login(lang):
    set_locale(lang)
    
    class LoginForm(RedirectForm):
        email = fields.TextField(_("E-mail"), [
            validators.Required(message=_("This field is required.")),
        ], widget=TextInput(autofocus=True, type="email"))
        password = fields.PasswordField(_("Password"), [
            validators.Required(message=_("This field is required.")),
        ])
    
    form = LoginForm(csrf_enabled=False)
    if request.method == "GET":
        if get_user():
            return redirect_back(url_for("language_root", lang=lang))
        return render_template("login.html", lang=lang, form=form)
    else: # POST
        try:
            if not form.validate():
                raise Error(_("Form did not have all fields filled correctly."))
            email = form.email.data
            password = form.password.data
            user = User.query.filter_by(email=email).first()
            if user:
                if user.has_password(password):
                    if user.has_email_verified():
                        logger.info("login ok")
                    else:
                        raise Error(_("The e-mail address is not yet verified."))
                else:
                    raise Error(_("The password you provided is incorrect."))
            else:
                raise Error(_("The e-mail you provided is not registered."))
            
            set_user(user)
            flash(_("You have been logged in."), category="info")
            return redirect_back(url_for("language_root", lang=lang))
        except Error as error:
            if request.is_xhr: # AJAX
                return jsonify(error=unicode(error))
            else:
                flash(unicode(error), category="error")
                return render_template("login.html", lang=lang, form=form)
