from flask_wtf import widgets
from flask import Markup

#class EmptyWidget():
    #def __call__(self, field):
        #return ""

class TextInput(widgets.TextInput):
    def __init__(self, **kwargs):
        super(TextInput, self).__init__()
        self.kwargs = kwargs
    
    def __call__(self, field, **kwargs):
        kwargs.update(self.kwargs)
        return super(TextInput, self).__call__(field, **kwargs)
    
class TextArea(widgets.TextArea):
    def __init__(self, **kwargs):
        super(TextArea, self).__init__()
        self.kwargs = kwargs
    
    def __call__(self, field, **kwargs):
        kwargs.update(self.kwargs)
        return super(TextArea, self).__call__(field, **kwargs)

class WikiareaWidget():
    def __init__(self, preview_position="bottom", top_html="", bottom_html=""):
        self.preview_position = preview_position
        self.top_html = top_html
        self.bottom_html = bottom_html
    def __call__(self, field):
        if field.data is None:
            field.data = ""
        preview = Markup('<span id="%(id)s-preview"></span>' % {"id": field.name})
        if self.preview_position == "bottom":
            top = self.top_html
            bottom = preview + self.bottom_html
        else:
            top = self.top_html + preview
            bottom = self.bottom_html
        return Markup("""
        %(top)s
        <div id="%(id)s-button-bar"></div>
        <textarea name="%(name)s" id="%(id)s-textarea" class="resizable">%(data)s</textarea>
        %(bottom)s
        
        <script type="text/javascript">
            $(document).ready(function() {
                wmdEditor = new WMDEditor({
                    input: "%(id)s-textarea",
                    button_bar: "%(id)s-button-bar",
                    preview: "%(id)s-preview",
                });
                $(document).trigger("wmd-ready", wmdEditor);
            });
            
            $('textarea.resizable').autoResize({
                animate: false,
                extraSpace: 16,
            });
        </script>
        """ % {"top": top, "bottom": bottom, "name": field.name, "id": field.name, "data": field.data})

class TagAutocompleteWidget():
    def __call__(self, field):
        return Markup("""
        <input type="text" id="%(id)s" class="autocomplete" name="%(name)s" />
        <script type="text/javascript">
            $("input.autocomplete").autocomplete({
                source: "/suggest/tags",
                minLength: 0
            });
        </script>
        """ % {"name": field.name, "id": field.name})

class SelectWidget():
    def __call__(self, field, ul_class='', **kwargs):
        kwargs.setdefault('type', 'radio')
        field_id = kwargs.pop('id', field.id)
        html = [u'<ul %s>' % widgets.html_params(id=field_id, class_=ul_class)]
        for value, label, checked in field.iter_choices():
            choice_id = u'%s-%s' % (field_id, value)
            options = dict(kwargs, name=field.name, value=value, id=choice_id)
            if checked:
                options['checked'] = 'checked'
            html.append(u'<li><input %s /> ' % widgets.html_params(**options))
            html.append(u'<label class="%s" for="%s"><span class="icon"></span> %s</label></li>' % (value, choice_id, label))
        html.append(u'</ul>')
        return Markup(u''.join(html))
