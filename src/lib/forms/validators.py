from flask import request
from wtforms import validators
from flask.ext.babel import gettext as _
from PIL import Image

#class RequiredWithoutAsterisk:
    #def __init__(self, message):
        #self.message = message
    #def __call__(self, form, field):
        #return validators.Required(message=self.message)(form, field)

class FileRequired:
    def __call__(self, form, field):
        if field.type == "FileField":
            if not request.files[field.name]:
                raise validators.StopValidation(message=_("This field is required."))
        else:
            return validators.Required(message=_("This field is required."))(form, field)

class ImageSize:
    def __init__(self, width, height):
        self.size = (width, height)
    def __call__(self, form, field):
        if request.files[field.name].filename != "":
            stream = request.files[field.name].stream
            stream.seek(0)
            try:
                image = Image.open(stream)
                if image.size != self.size:
                    raise validators.StopValidation(_("Image size %(s1)s is not allowed. Allowed image size is: %(s2)s.", s1="x".join(map(str, image.size)), s2="x".join(map(str, self.size))))
            except IOError:
                raise validators.StopValidation(_("Error occured while examining image file."))

class FileExtension:
    def __init__(self, extension):
        self.extension = extension
    def __call__(self, form, field):
        if request.files[field.name].filename != "":
            filename = request.files[field.name].filename
            if '.' not in filename:
                raise validators.StopValidation(_("File extension is missing."))
            extension = filename.rsplit('.', 1)[1]
            if extension != self.extension:
                raise validators.StopValidation(_("File extension %(e1)s is not allowed. Allowed extension is %(e2)s.", e1=extension, e2=self.extension))

class StrongPassword:
    def __call__(self, form, field):
        try:
            import cracklib
            try:
                cracklib.VeryFascistCheck(field.data.encode('utf8'))
            except ValueError, ex:
                message = ex.message
                if message == "it is too short":
                    message = _("it is too short")
                elif message == "it is WAY too short":
                    message = _("it is WAY too short")
                elif message == "is too simple":
                    message = _("is too simple")
                elif message == "it does not contain enough DIFFERENT characters":
                    message = _("it does not contain enough DIFFERENT characters")
                elif message == "it is based on a dictionary word":
                    message = _("it is based on a dictionary word")
                elif message == "it is based on a (reversed) dictionary word":
                    message = _("it is based on a (reversed) dictionary word")
                elif message == "it is too simplistic/systematic":
                    message = _("it is too simplistic/systematic")
                elif message == "it looks like a National Insurance number.": # e.g. JG121316A
                    message = _("it looks like a National Insurance number")
                elif message == "it is based on your username":
                    return # local OS user does not matter
                raise validators.StopValidation("%s." % message.capitalize())
        except ImportError:
            pass
        
class NotEqualTo:
    def __init__(self, fieldname, message):
        self.fieldname = fieldname
        self.message = message
    def __call__(self, form, field):
        if getattr(form, self.fieldname).data == field.data:
            raise validators.StopValidation(self.message)
