#autoimport
import os
from lib.assetwatch import assetwatch
from .app import app

assets_dir = os.path.dirname(__file__) + "/components"
public_dir = os.path.dirname(__file__) + "/static"
http_path = "/static"

app.jinja_env.globals["stylesheet_tag"] = lambda: assetwatch.stylesheet_tag()
app.jinja_env.globals["javascript_tag"] = lambda: assetwatch.javascript_tag()

def run_assetwatch():
    app.jinja_env.globals["stylesheet_tag"] = lambda: assetwatch.stylesheet_tag(debug=True, public_dir=public_dir)
    app.jinja_env.globals["javascript_tag"] = lambda: assetwatch.javascript_tag(debug=True, public_dir=public_dir)
    assetwatch.run(assets_dir, public_dir, http_path, debug=True)

def run_assetwatch_once():
    app.jinja_env.globals["stylesheet_tag"] = lambda: assetwatch.stylesheet_tag(debug=False, public_dir=public_dir)
    app.jinja_env.globals["javascript_tag"] = lambda: assetwatch.javascript_tag(debug=False, public_dir=public_dir)
    assetwatch.run_once(assets_dir, public_dir, http_path, debug=False)