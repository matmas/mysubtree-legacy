#autoimport
import logging
from datetime import timedelta
from flask import request, redirect, flash, url_for, g, jsonify, abort, Markup
from flask_wtf import Form
from wtforms import fields, validators, ValidationError
from flask.ext.babel import gettext as _, ngettext
from lib.time import utcnow
from lib.error import Error
from lib.flood_protection import limit
from lib.forms.widgets import TextInput
from lib.forms.keepempty import KeepEmpty
from lib.forms.validators import NotEqualTo
from lib.redirectback import redirect_back, will_redirect_to_route
from lib.remote_addr import remote_addr
from mysubtree.db import db
from mysubtree.backend.models.user import User, username_max_length, email_max_length, nickname_max_length
from mysubtree.backend.models import user
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.web.mail import send_email
from mysubtree.web.babel import set_locale
from mysubtree.web.user import get_user
from .. import password_validators

logger = logging.getLogger("web")

@app.route("/<lang>/create-account", methods=["GET", "POST"])
def create_account(lang):
    set_locale(lang)
    name_min_length = 2
    name_max_length = username_max_length
    nick_min_length = 2
    nick_max_length = nickname_max_length
    
    class NotTakenValidator:
        def __init__(self, field, already_registered_message, in_process_message):
            self.field = field
            self.already_registered_message = already_registered_message
            self.in_process_message = in_process_message
        def __call__(self, form, field):
            user = User.query.filter_by(**{self.field: field.data}).first()
            if user:
                if user.has_email_verified():
                    raise ValidationError(self.already_registered_message)
                elif utcnow() < user.date + timedelta(hours=24):
                    raise ValidationError(self.in_process_message)
                else:
                    db.session.delete(user)
                    db.session.commit()
    
    class CreateAccountForm(Form):
        nick = fields.TextField(_("Nickname"), [
            validators.Required(message=_("This field is required.")),
            validators.Length(min=nick_min_length, message=ngettext("Field must be at least %(num)s character long.", "Field must be at least %(num)s characters long.", nick_min_length)),
            validators.Length(max=nick_max_length, message=ngettext("Field cannot be longer than %(num)s character.", "Field cannot be longer than %(num)s characters.", nick_max_length)),
            validators.Regexp(r'^\w+$', message=_("Nickname must not contain characters other than unaccented letters and numbers.")),
            NotTakenValidator("nick", _("Such nickname is already registered."), _("Such nickname is just in the process of being registered.")),
        ], widget=TextInput(autofocus=True))
        name = fields.TextField(_("Your name"), [
            validators.Required(message=_("This field is required.")),
            validators.Length(min=name_min_length, message=ngettext("Field must be at least %(num)s character long.", "Field must be at least %(num)s characters long.", name_min_length)),
            validators.Length(max=name_max_length, message=ngettext("Field cannot be longer than %(num)s character.", "Field cannot be longer than %(num)s characters.", name_max_length)),
        ])
        email = fields.TextField(_("Your e-mail"), [
            validators.Required(message=_("This field is required.")),
            validators.Length(max=email_max_length, message=ngettext("Field cannot be longer than %(num)s character.", "Field cannot be longer than %(num)s characters.", email_max_length)),
            validators.Email(message=_("Invalid e-mail address.")),
            NotTakenValidator("email", _("Such e-mail address is already registered."), _("Such e-mail address is just in the process of being registered.")),
        ], widget=TextInput(type="email"))
        password = fields.PasswordField(_("Password"), password_validators.get_password_validators() + [
            NotEqualTo("name", _("Password can't be identical to your name"))
        ])
        password_again = fields.PasswordField(_("Repeat password"), [
            validators.Required(message=_("This field is required.")),
            validators.EqualTo("password", message=_("Passwords must match")),
        ])
        agree = fields.BooleanField(Markup(_('I agree to the {0}Terms of Use{1}.').format('<a href="%s" target="_blank">' % url_for("terms", lang="en"), "</a>")), [validators.Required(message=_("This field is required."))])
        keepempty = KeepEmpty()
        
    
    form = CreateAccountForm()
    if request.method == "GET":
        if get_user():
            if will_redirect_to_route(app, "login"):
                return redirect(url_for("language_root", lang=lang)) # prevent redirect loop login->create_account->login->...
            else:
                return redirect_back(url_for("language_root", lang=lang))
        return render_template("create_account.html", lang=lang, form=form)
    else: # POST
        if g.is_ajax: # just for form validation
            fieldname = request.form.get("validate_field")
            field = form._fields.get(fieldname)
            if not field:
                return ""
            field.validate(form)
            message = ""
            if fieldname == "email":
                message = _("We'll send you a confirmation.")
            return render_template("int/errors/errors.html", message=message, field=field)
        else:
            try:
                if not form.validate():
                    raise Error(_("Form did not have all fields filled correctly."))
                
                #limit(remote_addr(), num_requests=1, num_seconds=60)
                user = User()
                user.email = form.email.data
                #limit(user.email, num_requests=1, num_seconds=3600)
                user.code = user.generate_code()
                user.date = utcnow()
                user.name = form.name.data
                user.nick = form.nick.data
                user.set_password(form.password.data)
                db.session.add(user)
                db.session.commit()
                
                if app.config['DEBUG'] or app.config['TESTING']:
                    verification_url = url_for("verify", lang=lang, code=user.code, _external=True)
                else:
                    verification_url = app.config["BASE_URL"] + url_for("verify", lang=lang, code=user.code)
                message = _("Use the following link within 24 hours to complete your account creation:") + "\n" + verification_url
                subject = "%s e-mail verification" % app.config["APP_NAME"]
                send_email(user.email, subject, message)
                
                flash(_("An e-mail has been sent to you containing verification instructions. Please follow them before continuing."), category="info")
                logger.info("account created")
                return redirect(url_for("language_root", lang=lang))
            except Error as error:
                if request.is_xhr: # AJAX
                    return jsonify(error=unicode(error))
                else:
                    flash(unicode(error), category="error")
                return render_template("create_account.html", lang=lang, form=form)
        
