#autoimport
import logging
from datetime import datetime, timedelta
from flask import redirect, flash, url_for
from flaskext.babel import gettext as _
from mysubtree.web.app import app
from mysubtree.db import db
from mysubtree.backend.models.node.node import Node
from mysubtree.backend.models.user import User
from mysubtree.backend.models.node.types.all import get_model
from mysubtree.web.user import set_user
from mysubtree.web.babel import set_locale

logger = logging.getLogger("web")

@app.route("/<lang>/verify/<code>")
def verify(lang, code):
    set_locale(lang)
    user = User.query.filter_by(code=code).first()
    if user:
        if not user.has_email_verified():
            usernode = get_model("users")(username=user.name, alias=user.nick)
            db.session.add(usernode)
            user.node = usernode.id
            
            db.session.add(user)
            db.session.commit()
            
            set_user(user)
            
            flash(_("E-mail was successfully verified."), category="info")
            logger.info("account verified")
            return redirect(url_for("language_root", lang=lang))
        else:
            flash(_("E-mail is already verified."), category="error")
    else:
        flash(_("Invalid verification code."), category="error")
        logger.info("verification code not found")
    return redirect(url_for("language_root", lang=lang))
