#from flask import Blueprint, render_template

print __name__

def init(app):
    relative_templates = Blueprint('relative_templates', __name__, template_folder='templates')
    #return render_template('pages/%s.html' % page)
    