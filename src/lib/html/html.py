# caveat: "element_name" and "html" attributes are not possible, e.g. <span html="something">...
from flask import escape, Markup
from .component_node import ComponentNode
from .code_generator import generate_code
from . import is_debug

class Html:
    
    def __init__(self):
        self.data = []
        self.unapplied = None
        
        self.root_element = Element("", None)
        self.current_element = self.root_element
        
        self.root_componentnode = ComponentNode(None)
    
    def _apply_unapplied(self):
        if self.unapplied:
            self.unapplied.finish()
    
    def text(self, text):
        self._apply_unapplied()
        self._text(text)
    
    def _text(self, text):
        self.data.append(unicode(escape(text)))
    
    def __str__(self):
        self._apply_unapplied()
        
        if is_debug():
            self._build_component_tree(self.root_element, self.root_componentnode)
            generate_code(self.root_componentnode)
        
        return "".join(self.data)
    
    def add(self, html):
        self._apply_unapplied()
        html._apply_unapplied()
        
        for child in html.root_element.children:
            self.current_element.append(child)
        
        self.data.extend(html.data)
    
    def element(self, element_name, **kwargs):
        self._apply_unapplied()
        return Element(element_name, html=self, **kwargs)
    
    def div(self, **kwargs):
        return self.element("div", **kwargs)
    
    def span(self, **kwargs):
        return self.element("span", **kwargs)
    
    def h1(self, **kwargs):
        return self.element("h1", **kwargs)
    
    def a(self, **kwargs):
        return self.element("a", **kwargs)
    
    def ul(self, **kwargs):
        return self.element("ul", **kwargs)
    
    def li(self, **kwargs):
        return self.element("li", **kwargs)
    
    def form(self, **kwargs):
        return self.element("form", **kwargs)
    
    def small(self, **kwargs):
        return self.element("small", **kwargs)
    
    def b(self, **kwargs):
        return self.element("b", **kwargs)
    
    def img(self, **kwargs):
        return self.element("img", **kwargs)
    
    def input(self, **kwargs):
        return self.element("input", **kwargs)
    
    def table(self, **kwargs):
        return self.element("table", **kwargs)
    
    def tbody(self, **kwargs):
        return self.element("tbody", **kwargs)
    
    def tr(self, **kwargs):
        return self.element("tr", **kwargs)
    
    def td(self, **kwargs):
        return self.element("td", **kwargs)
    
    
    def _build_component_tree(self, element, current_componentnode):
        if element.kwargs.get("component") == True:
            current_componentnode = current_componentnode.ensure_and_get_child_of(element)
        for child_element in element.children:
            self._build_component_tree(child_element, current_componentnode)
    

class Element:
    def __init__(self, element_name, html, **kwargs):
        self.name = element_name
        self.kwargs = kwargs
        if html:
            self.html = html
            assert self.html.unapplied == None
            self.html.unapplied = self
        
        self.parent = None
        self.children = []

    def attributes(self):
        special_attributes = ["component", "lazy"] # they will not be sent to browser
        def fix_kwarg_key(key):
            if key == "class_":
                return "class"
            return key
        def fix_kwarg_value(value):
            if type(value) == list:
                return " ".join(value).strip()
            return value
        attributes = "".join(" %s='%s'" % (fix_kwarg_key(key), fix_kwarg_value(value)) for key, value in self.kwargs.items() if key not in special_attributes)
        return attributes
    
    def opening_tag(self):
        return Markup("<%s%s>" % (self.name, self.attributes()))
    
    def closing_tag(self):
        return Markup("</%s>" % self.name)
    
    def __enter__(self):
        self.html.unapplied= None
        
        self.html.current_element.append(self)
        self.html.current_element = self
        if not self.kwargs.get("lazy"):
            self.html._text(self.opening_tag())
        return self

    def __exit__(self, type, value, traceback):
        self.html.current_element = self.html.current_element.parent
        if not self.kwargs.get("lazy"):
            self.html._text(self.closing_tag())
        return False
    
    def finish(self):
        self.html.unapplied = None
        self.html._text(Markup("<%s%s />" % (self.name, self.attributes())))
        
    def append(self, element):
        self.children.append(element)
        element.parent = self
    
    def get_classes(self):
        class_ = self.kwargs.get("class_", "")
        if type(class_) == list:
            return class_
        else:
            return class_.split()
    
    def __str__(self):
        return self.name + " " + ", ".join(self.get_classes())

    def dump_recursively(self, indentation=0):
        print indentation * "  " + str(self)
        for child in self.children:
            child.dump_recursively(indentation + 1)
    
    def get_path(self):
        element = self
        path = []
        while element is not None:
            path.append(element)
            element = element.parent
        path.reverse()
        return path
    
    def is_similar_to(self, other):
        return self.name == other.name and self.get_classes()[0] == other.get_classes()[0]