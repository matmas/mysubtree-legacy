from mysubtree.db import autoimport_and_init_db
from mysubtree.web.app import app

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/mysubtree"
app.config["CACHE_NO_NULL_WARNING"] = True

autoimport_and_init_db()
