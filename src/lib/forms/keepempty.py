from wtforms import fields, validators
from flask import Markup
from flask.ext.babel import gettext as _


def KeepEmpty():
    return fields.HiddenField(_("Keep empty"), [_must_be_empty_validator], widget=_keep_empty_widget)


def _keep_empty_widget(field):
    return Markup("""
    <div class="keepempty">
        %(label)s: <input type="text" id="%(id)s" name="%(name)s" />
    </div>
    """ % {"label": _("Keep empty"), "name": field.name, "id": field.name})


def _must_be_empty_validator(form, field):
    if field.data:
        raise validators.StopValidation(_("This field must be empty."))

