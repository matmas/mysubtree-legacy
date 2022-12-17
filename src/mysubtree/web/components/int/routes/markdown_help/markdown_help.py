#autoimport
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.web.babel import set_locale


@app.route("/<lang>/editing-help")
def markdown_help(lang):
    set_locale(lang)
    return render_template("markdown_help.html")

