#autoimport
from werkzeug.routing import BaseConverter
from mysubtree.web.app import app
from mysubtree.backend import common

#class RegexConverter(BaseConverter):
    #def __init__(self, url_map, regex):
        #super(RegexConverter, self).__init__(url_map)
        #self.regex = regex
    #def to_python(self, value):
        #return value
    #def to_url(self, value):
        #return value
#app.url_map.converters["regex"] = RegexConverter

class AlphanumConverter(BaseConverter):
    def __init__(self, url_map):
        super(AlphanumConverter, self).__init__(url_map)
        self.regex = "[a-zA-Z0-9]+"
    def to_python(self, value):
        return value
    def to_url(self, value):
        return value
app.url_map.converters["alphanum"] = AlphanumConverter
