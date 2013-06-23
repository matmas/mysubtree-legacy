#autoimport
from datetime import timedelta
from flask import request, redirect, flash, url_for
from flaskext.babel import gettext as _
from flask_wtf import Form, fields, validators
from lib.wtforms.widgets import TextInput
from lib.time import utcnow
from lib.error import Error
from lib.flood_protection import limit
from lib.remote_addr import remote_addr
from mysubtree.backend.models.user import User
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.db import db
from mysubtree.web.mail import send_email
from mysubtree.web.babel import set_locale

@app.route("/<lang>/forgot", methods=["GET", "POST"])
def forgot(lang):
    set_locale(lang)
    
    class ForgotForm(Form):
        email = fields.TextField(_("E-mail"), [
            validators.Required(message=_("This field is required.")),
        ], widget=TextInput(autofocus=True, type="email"))
    form = ForgotForm(csrf_enabled=False)
    
    if request.method == "GET":
        return render_template("forgot.html", lang=lang, form=form)
    else: # POST
        try:
            if not form.validate():
                raise Error(_("Form did not have all fields filled correctly."))
            
            #limit(remote_addr(), num_requests=10, num_seconds=60)
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                #limit(remote_addr(), num_requests=1, num_seconds=60)
                #limit(user.email, num_requests=1, num_seconds=3600)
                if user.reset_date and utcnow() < user.reset_date + timedelta(hours=24):
                    raise Error(_("The e-mail has already been sent."))
                user.reset_code = user.generate_code()
                user.reset_date = utcnow()
                
                if app.config['TESTING']:
                    reset_url = url_for("reset", lang=lang, code=user.reset_code, _external=True)
                else:
                    verification_url = app.config["BASE_URL"] + url_for("reset", lang=lang, code=user.reset_code)
                
                message = _("Use the following link within 24 hours to reset your password:") + "\n" + reset_url
                subject = "%s password reset" % app.config["APP_NAME"]
                send_email(user.email, subject, message)
                db.session.commit()
                flash(_("An e-mail has been sent to you containing password reset instructions."), category="info")
                return redirect(url_for("language_root", lang=lang))
            else:
                raise Error(_("The e-mail you provided is not registered."))
        except Error as error:
            flash(unicode(error), category="error")
            return render_template("forgot.html", lang=lang, form=form)
