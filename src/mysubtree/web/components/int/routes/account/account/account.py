#autoimport
from mysubtree.web.babel import set_locale
from mysubtree.web.app import app
from mysubtree.web.templating import render_template

@app.route("/<lang>/account")
def account(lang):
    set_locale(lang)
    return render_template("account.html", lang=lang)
 
