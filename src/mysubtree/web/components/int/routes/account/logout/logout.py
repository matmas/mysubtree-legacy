#autoimport
import logging
from flask import redirect, flash, url_for, session
from flask.ext.babel import gettext as _
from lib.redirectback import redirect_back
from mysubtree.web.app import app
from mysubtree.web.babel import set_locale

logger = logging.getLogger("web")

@app.route("/<lang>/logout")
def logout(lang):
    set_locale(lang)
    session.clear()
    logger.info("logout")
    flash(_("You have been logged out."), category="info")
    return redirect_back(url_for("login", lang=lang))
 
