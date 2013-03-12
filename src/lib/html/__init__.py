_output_path = None

def get_output_path():
    return _output_path

def set_output_path(output_path):
    global _output_path
    _output_path = output_path

_debug = None

def is_debug():
    return _debug

def set_debug(debug):
    global _debug
    _debug = debug

from .html import Html
