#autoimport
from mysubtree.web.app import app
from mysubtree.web.templating import render_template

@app.route("/")
def home():
    return render_template("home.html")

