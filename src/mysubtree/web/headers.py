#autoimport
from urlparse import urlparse, urlunparse
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

    # # Make all redirects with relative URLs
    # if "Location" in response.headers:
    # 	u = list(urlparse(response.headers["Location"]))
    # 	u[0] = None # scheme
    # 	u[1] = None # netloc
    # 	relative_url = urlunparse(u)
    # 	assert relative_url.startswith("/")
    # 	# response.headers["Location"] = relative_url
    response.autocorrect_location_header = False	

    return response