import sys, os
sys.path.append(os.path.dirname(__file__)) # to be able to import our modules
from mysubtree import config
config.debug = False
#===============================================================================

import logging
from lib.logginghandlers import CarefulSMTPHandler
from mysubtree.web.app import app
from mysubtree.db import autoimport_and_init_db
from mysubtree.backend.live.live import enable_live
from mysubtree.web.assetwatch import run_assetwatch_once
from mysubtree.decrementer.decrementer import run_decrementer

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/"
app.config["SQLALCHEMY_POOL_RECYCLE"] = 3600

app.config["CACHE_TYPE"] = "memcached"
app.config["CACHE_MEMCACHED_SERVERS"] = ["127.0.0.1:11211"]
app.config["CACHE_DEFAULT_TIMEOUT"] = 3600

autoimport_and_init_db()

run_assetwatch_once()

enable_live()

#run_decrementer()

# Logging exceptions to e-mail:
mail_handler = CarefulSMTPHandler("127.0.0.1", "mysubtree@mysubtree.org", ["riesz.martin@gmail.com"], "Mysubtree exception occured!")
mail_handler.setLevel(logging.ERROR)
app.logger.addHandler(mail_handler)

app.config["EMAIL_ADDRESS"] = "noreply@mysubtree.org"

application = app # must be named application because of WSGI

if __name__ == "__main__":
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop
    
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()
