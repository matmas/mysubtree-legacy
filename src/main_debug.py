import os
import logging
import sys
from flask_debugtoolbar import DebugToolbarExtension
from lib.files import get_files_recursively
from mysubtree.web.app import app
from mysubtree.web.assetwatch import run_assetwatch
from mysubtree.web.codegenerator import enable_codegenerator
from mysubtree.db import autoimport_and_init_db
from mysubtree.backend.live.live import enable_live

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    
    from mysubtree.web import logger # enable web logger
    
    from mysubtree import config
    config.debug = True
    
    # Enable Debug Toolbar
    app.debug = True
    
    # Specify the debug panels you want
    app.config['DEBUG_TB_PANELS'] = [
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
        # Add the line profiling
        #'flask_debugtoolbar_lineprofilerpanel.panels.LineProfilerPanel'
    ]
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI") or "postgresql:///mysubtree"
    #app.config["SQLALCHEMY_ECHO"] = True
    
    #from werkzeug.contrib.profiler import ProfilerMiddleware
    #f = open("profiler.log", "w")
    #app.wsgi_app = ProfilerMiddleware(app.wsgi_app, f)
    
    #app.config["CACHE_TYPE"] = "simple"
    app.config["CACHE_TYPE"] = "memcached"
    app.config["CACHE_MEMCACHED_SERVERS"] = ["127.0.0.1:11211"]
    app.config["CACHE_DEFAULT_TIMEOUT"] = 3600
    
    autoimport_and_init_db()
    
    #enable_codegenerator()
    
    enable_live()
    
    run_assetwatch()
    
    print " *"
    try:
        host = sys.argv[1]
    except IndexError:
        host = "127.0.0.1"
    app.run(host=host, debug=True,
        extra_files=get_files_recursively(directory=".", suffix=".html") # restart server on .html files changes to ensure all templates referencing each other are found
    )
