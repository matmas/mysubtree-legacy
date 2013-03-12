#autoimport
from .app import app

@app.after_request
def after_request(response):
    
    # Enable support for Google Chrome Frame plugin in IE:
    response.headers["X-UA-Compatible"] = "chrome=1"
    
    # Enable Clickjacking protection (prevents loading within a frame)
    response.headers["X-Frame-Options"] = "deny"
    
    # Notifications and flash messages must not be reshown when user hits the back button:
    response.headers["Cache-Control"] = "no-cache, no-store, max-age=0, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "Fri, 01 Jan 1990 00:00:00 GMT"
    return response