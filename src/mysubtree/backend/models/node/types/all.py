import os
from lib.camelcase import dash_to_camelcase

def get_model(type):
    return _get_class("%(package)s.%(module)s.%(class)s" % {
        "package": __package__,
        "module": type.replace("-", "_"),
        "class": dash_to_camelcase(type)
    })

def get_all_types():
    types = []
    for dir, dirs, filenames in os.walk(os.path.dirname(__file__)):
        for filename in filenames:
            file = os.path.join(dir, filename)
            this_file = __file__.rstrip(".py").rstrip(".pyc") + ".py" # sometimes __file__ ends with .pyc
            if (filename.endswith(".py") and filename != "__init__.py" and
                file != this_file):
                type = filename.rstrip(".py").replace("_", "-") # TODO: replace rstrip with correct approach (endswith + [:-len(...)]
                types.append(type)
    return types

# From http://stackoverflow.com/a/452981/682025
def _get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m

