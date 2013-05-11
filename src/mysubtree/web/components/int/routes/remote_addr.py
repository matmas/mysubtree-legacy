#autoimport
from mysubtree.web.app import app
from lib.remote_addr import remote_addr as get_remote_addr

@app.route("/remote_addr")
def remote_addr():
    return get_remote_addr()
