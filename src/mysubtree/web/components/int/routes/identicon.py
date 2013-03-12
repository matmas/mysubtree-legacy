##autoimport
#import StringIO
#from datetime import datetime, timedelta
#from flask import request, make_response, abort
#from ext.visicon import Visicon
#from mysubtree.web.app import app

#supported_sizes = [14]

#@app.route("/identicon/<md5hash>/<int:size>")
#def identicon(md5hash, size):
    #if len(md5hash) != 32 or not all(c in "0123456789abcdef" for c in md5hash):
        #abort(403)
    #if size not in supported_sizes:
        #abort(404)
    #buffer = StringIO.StringIO()
    #Visicon.min_size = min(supported_sizes)
    #Visicon(hash=md5hash, size=size).draw_image().save(buffer, format="PNG")
    #output = buffer.getvalue()
    #buffer.close()
    #response = make_response(output)
    #response.mimetype = "image/png"
    #response.expires = datetime.utcnow() + timedelta(days=365)
    #response.cache_control.public = True
    #return response