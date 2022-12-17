#autoimport
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from os.path import dirname


@app.route("/throw-exception")
def throw_exception():
    something_nonexistent


@app.errorhandler(404)
def page_not_found(e):
    return render_template("static/404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("static/50x.html"), 500
