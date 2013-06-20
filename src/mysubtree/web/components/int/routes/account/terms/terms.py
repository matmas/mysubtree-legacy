#autoimport
import os.path, time
from mysubtree.web.app import app
from mysubtree.web.templating import render_template
from mysubtree.web.babel import set_locale

@app.route("/<lang>/terms")
def terms(lang):
    set_locale(lang)
    template = "terms.html"
    template_file = os.path.join(os.path.dirname(__file__), template)
    variables = {
        "DOMAIN": "mysubtree.org",
        "COMPANY_NAME": "Matmas",
        "COUNTRY": "Sweden",
        "last_updated": time.strftime("%b %d, %Y", time.gmtime(os.path.getmtime(template_file))),
    }
    return render_template(template, lang=lang, **variables)

