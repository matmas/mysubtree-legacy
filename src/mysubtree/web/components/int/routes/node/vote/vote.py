#autoimport
from flask import request, flash
from flask_wtf import Form
from flaskext.babel import gettext as _
from lib.redirectback import RedirectForm, redirect_back
from lib.error import Error
from lib.wtforms.keepempty import KeepEmpty
from lib.remote_addr import remote_addr
from mysubtree.backend import backend
from mysubtree.backend.models.node.node_voting import you_like_it_already, no_like_to_undo
from mysubtree.db import db
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.web.babel import set_locale
from mysubtree.web.components.int.routes.middleware.ajax_response import ajax_response
from mysubtree.web.components.int.routes.middleware.refresh_account import refresh_account

@app.route("/vote/<nid>", methods=["GET", "POST"])
@ajax_response
@refresh_account
def vote(nid):
    node = backend.get_node_from(nid)
    set_locale(node.lang)
    class VoteForm(RedirectForm):
        keepempty = KeepEmpty()
    
    likeform = VoteForm()
    undoform = VoteForm()
    
    if request.method == "GET":
        if not node.is_likable_by_current_user():
            likeform = None
        if not node.is_likable_by_current_user(is_undo=True):
            undoform = None
        
        return render_template("vote.html", node=node, lang=node.lang, likeform=likeform, undoform=undoform)
    else: # POST
        try:
            is_undo = "undo" in request.args
            if not VoteForm().validate():
                raise Error(_("Form did not have all fields filled correctly."))
            
            # default values for AJAX in case of passable exception:
            relative_value = 0
            is_votenode_created = False
            
            relative_value, is_votenode_created = node.vote(is_undo)
            assert relative_value != 0
            db.session.commit()
            
        except Error as error:
            if request.is_xhr: # AJAX
                if error == Error(you_like_it_already()):
                    pass # no need to alert user with message, just change button state to pressed
                elif error == Error(no_like_to_undo()):
                    pass # no need to alert user with message, just change button state to unpressed
                else:
                    return {"error": unicode(error)}
            else:
                flash(unicode(error), category="error")
                return redirect_back(node.url())
        
        if request.is_xhr: # AJAX
            return {
                "voting": {
                    "nid": node.nid(),
                    "relative_value": "%+d" % relative_value,
                    "is_votenode_created": is_votenode_created,
                    "ipaddress": remote_addr(),
                }
            }
        
        if not is_undo:
            flash(_("Voted sucessfully."), category="info")
        else:
            flash(_("You sucessfully undid your vote."), category="info")
        return redirect_back(node.url())

