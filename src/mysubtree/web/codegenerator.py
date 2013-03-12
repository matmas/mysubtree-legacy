import os
from lib import html

def enable_codegenerator():
    html.set_output_path(os.path.dirname(__file__) + "/components/ext/generated_code.js")
    html.set_debug(True)
