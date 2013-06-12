#autoimport
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.web.babel import set_locale

@app.route("/<lang>/terms")
def terms(lang):
    set_locale(lang)
    variables = {
        "DOMAIN": "mysubtree.org",
        "COMPANY_NAME": "Mysubtree",
        "STATE": "United States",
        "COUNTRY": "California",
        
    }
    return render_template("terms.html", lang=lang, **variables)

