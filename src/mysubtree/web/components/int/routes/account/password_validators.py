from flask_wtf import validators
from flaskext.babel import gettext as _, ngettext
from lib.wtforms.validators import StrongPassword

def get_password_validators(): # for create account and reset password
    password_min_length = 8
    return [
        validators.Length(min=password_min_length, message=ngettext("Field must be at least %(num)s character long.", "Field must be at least %(num)s characters long.", password_min_length)),
        StrongPassword(),
        validators.Required(message=_("This field is required.")), # after StrongPassword to get more helpful messages - because it does considers whitespace-filled field as empty
    ]
