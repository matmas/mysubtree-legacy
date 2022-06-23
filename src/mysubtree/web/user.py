import traceback
from flask import session, g, request
from mysubtree.backend.models.user import User
from mysubtree.web.app import app
from mysubtree.web.cache import cache


def set_user(user):
    session["user_id"] = user.id
    g.current_user = user


def get_user():
    try:
        user = getattr(g, "current_user", None)
        if not user:
            id = session.get("user_id")
            if id:
                user = get_user_from_db(id)
                g.current_user = user
                assert getattr(g, "current_user") == user
    except RuntimeError:
        user = None  # out of request context
    return user


def get_user_node():
    return get_user().node if get_user() else None


def get_user_name():
    return get_user().name if get_user() else None


def get_nick_name():
    return get_user().nick if get_user() else None


#@cache.memoize()
def get_user_from_db(id):
    return User.query.get(id)