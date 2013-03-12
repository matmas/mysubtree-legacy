from sqlalchemy.event import listen
from sqlalchemy.orm import mapper
import inspect

#def on(event):
    #"""
    #Usage:
    #@on("before_insert")
    #def before_insert(self):
        #...
    #"""
    #class_name = inspect.stack()[1][3]
    #def decorator(fn):
        #def listener(mapper, connection, target):
            #if class_name == target.__class__.__name__: # TODO: *very* fragile (assumes class names will not collide)
                #fn(target)
        #listen(mapper, event, listener)
        #return fn
    #return decorator

#def on2(event, call):
    #"""
    #Usage:
    #@on("before_insert", call="validate")
    #class Test:
        #...
        #def validate(self):
            #...
    #"""
    #def class_decorator(cls):
        #fn = cls.__dict__.get(call)
        #def listener(mapper, connection, target):
            #if cls == target.__class__.__name__:
                #fn(target)
        #listen(mapper, event, listener)
        #return cls
    #return class_decorator
    

#def on_session(db, event):
    #class_name = inspect.stack()[1][3]
    #def decorator(fn):
        #def listener(session, instance):
            #fwefew
            #if instance.__class__.__name__ == class_name:
                #fn(instance)
            #return instance
        #listen(db.session.__class__, event, listener)
        #return fn
    #return decorator