virtualenv = "/home/matmas/.venv"
debug = True

def activate_enviroment():
    activate_this = virtualenv + "/bin/activate_this.py"
    execfile(activate_this, dict(__file__=activate_this))
    import sys
    import logging
    sys.stdout = sys.stderr
    logging.basicConfig(stream=sys.stderr)
    
    class DummyStdin():
        def close(self):
            pass
    sys.stdin = DummyStdin() # multiprocessing wants to close it what mod_wsgi does not allow