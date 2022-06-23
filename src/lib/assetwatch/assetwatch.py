import os
from os.path import dirname, abspath
import sys
if __name__ == "__main__":
    src_dir = dirname(dirname(dirname(abspath(__file__))))
    sys.path.append(src_dir)

#===============================================================================

from flask import url_for, Markup
from lib import process
from assetobserver import assetobserver, get_registers

if __name__ == "__main__":
    assets_dir = sys.argv[1]
    public_dir = sys.argv[2]
    http_path = sys.argv[3]
    environment = sys.argv[4]
    
    process.exit_if_another_instance("assetwatch")
    try:
        assetobserver(assets_dir, public_dir, http_path, environment)
    except KeyboardInterrupt:
        pass

_SUBDIR = "generated"


def run(assets_dir, public_dir, http_path, debug=True):
    public_dir += "/%s" % _SUBDIR
    http_path += "/%s" % _SUBDIR
    process.run_in_background([sys.executable, __file__, assets_dir, public_dir, http_path, "development" if debug else "production"])


def run_once(assets_dir, public_dir, http_path, debug=False):
    public_dir += "/%s" % _SUBDIR
    http_path += "/%s" % _SUBDIR
    get_registers(assets_dir, public_dir, http_path, "development" if debug else "production")


def stylesheet_tag(debug=False, public_dir=None):
    stylesheet_url = url_for("static", filename="%s/output_css/combined_screen.css" % _SUBDIR)
    return Markup('<link type="text/css" rel="stylesheet" href="%s" />' % stylesheet_url)


def javascript_tag(debug=False, public_dir=None):
    tags = []
    if debug and public_dir:
        path = os.path.join(public_dir, _SUBDIR, "input_js")
        for root, dirs, files in os.walk(path):
            files.sort()
            for filename in files:
                file = os.path.join(path, filename)
                javascript_url = url_for("static", filename=file[len(public_dir) + 1:])
                tags.append('<script type="text/javascript" src="%s"></script>' % javascript_url)
    else:
        javascript_url = url_for("static", filename="%s/combined.js" % _SUBDIR)
        tags = ['<script type="text/javascript" src="%s"></script>' % javascript_url]
    return Markup("\n".join(tags))
