#autoimport
from flask import request, flash, redirect, g, jsonify, abort
from flask_wtf import Form
from flask.ext.babel import gettext as _
from lib.redirectback import RedirectForm, redirect_back
from lib.error import Error
from lib.forms.keepempty import KeepEmpty
from mysubtree.backend import backend
from mysubtree.backend.models.node.node_flagging import you_already_sent_the_feedback, you_already_undid_your_feedback
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.db import db
from mysubtree.web.babel import set_locale
from mysubtree.web.user import get_user_node


@app.route("/flag/<nid>", methods=["GET", "POST"])
def flag(nid):
    node = backend.get_node_from(nid)
    set_locale(node.lang)
    class VoteForm(RedirectForm):
        keepempty = KeepEmpty()
    flagform = VoteForm()
    undoform = VoteForm()
    if request.method == "GET":
        if not node.is_really_flaggable_by_current_user():
            flagform = None
        if not node.is_really_flaggable_by_current_user(is_undo=True):
            undoform = None
        return render_template("flag.html", node=node, lang=node.lang, flagform=flagform, undoform=undoform)
    else: # POST
        try:
            if not VoteForm().validate():
                raise Error(_("Form did not have all fields filled correctly."))
            is_undo = "undo" in request.args
            
            relative_value = 0 # default in case there is an exception
            relative_value = node.flag(is_undo)
            if relative_value != 0:
                db.session.commit()
            
        except Error as error:
            if request.is_xhr: # AJAX
                if error == Error(you_already_sent_the_feedback()):
                    pass
                elif error == Error(you_already_undid_your_feedback()):
                    pass
                else:
                    return jsonify(error=unicode(error))
            else:
                flash(unicode(error), category="error")
                return redirect_back(node.url())
        
        if request.is_xhr: # AJAX
            return jsonify({"relative_value": relative_value})
        
        if relative_value == +1:
            flash(_("Thank you for the feedback."), category="info")
        if relative_value == -1:
            flash(_("You undid your feedback."), category="info")
        return redirect_back(node.url())
