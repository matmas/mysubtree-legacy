#autoimport
from os.path import dirname, abspath
import sys
if __name__ == "__main__":
    src_dir = dirname(dirname(dirname(abspath(__file__))))
    sys.path.append(src_dir)
    from mysubtree import config
    config.activate_enviroment()
#===============================================================================
import time
#from datetime import timedelta
from lib import process
from lib.time import utcnow
from mysubtree.backend.models.decrement import Decrement
from mysubtree.db import db
from mysubtree.web.app import app

@app.before_request
def decrement_if_needed():
    now = utcnow()
    for decrement in Decrement.query.filter(Decrement.at < now):
        db.session.connection().execute(
            "UPDATE node SET "+decrement.counter+" = "+decrement.counter+" - %(amount)s "
            "WHERE id = %(id)s AND type = %(type)s",
            {
                "amount": decrement.amount,
                "id": decrement.node,
                "type": decrement.type,
            }
        )
        db.session.connection().execute(
            "DELETE FROM decrement "
            "WHERE node = %(node)s AND type = %(type)s AND counter = %(counter)s AND at = %(at)s",
            {
                "node": decrement.node,
                "type": decrement.type,
                "counter": decrement.counter,
                "at": decrement.at,
            }
        ) # db.session.delete(decrement) does not work for some reason


def start_decrementing():
    process.exit_if_another_instance("mysubtree_decrementer")
    print("Decrementer running...")
    try:
        while True:
            decrement_if_needed()
            db.session.commit()
            time.sleep(30)
    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    app.config["SQLALCHEMY_DATABASE_URI"] = sys.argv[1]
    start_decrementing()


def run_decrementer():
    process.run_in_background([sys.executable, __file__, app.config["SQLALCHEMY_DATABASE_URI"]])
