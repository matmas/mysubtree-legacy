#autoimport
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.web.babel import set_locale


@app.route("/<lang>/about")
def about(lang):
    set_locale(lang)
    return render_template("about.html")

