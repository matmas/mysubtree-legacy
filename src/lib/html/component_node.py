from lib.camelcase import dash_to_camelcase

class ComponentNode():
    def __init__(self, element):
        self.parent = None
        self.children = []
        self.element = element
    
    def append(self, componentnode):
        self.children.append(componentnode)
        componentnode.parent = self
    
    def __str__(self):
        return str(self.element)
    
    def dump_tree(self, indentation=0):
        output = []
        output.append("// " + indentation * "    " + dash_to_camelcase(self.element.get_classes()[0], lower=True) + "\n")
        for child in self.children:
            output.append(child.dump_tree(indentation + 1))
        return "".join(output)

    def get_child_of(self, element):
        for child in self.children:
            if child.element.is_similar_to(element):
                return child
        return None
    
    def ensure_and_get_child_of(self, element):
        child = self.get_child_of(element)
        if not child:
            child = ComponentNode(element)
            self.append(child)
        return child

    def get_subpath_to(self, to_element):
        subpath = []
        #print str(self.element), "in", str(to_element)
        assert self.element in to_element.get_path()
        for element in to_element.get_path()[to_element.get_path().index(self.element) + 1:]:
            subpath.append(element)
        return subpath
    
    def get_subpath(self):
        return self.parent.get_subpath_to(self.element)
    
    def get_subselector(self):
        subselector = []
        for element in self.get_subpath():
            subselector.append(".children('%s.%s')" % (element.name, element.get_classes()[0]))
        return "".join(subselector)

    def get_generated_codes(self):
        codes = []
        
        code = []
        css_class = self.element.get_classes()[0]
        js_class = dash_to_camelcase(css_class)
        code.append("var %s = function(elem) {\n" % js_class)
        code.append("    this.$ = $(elem).closest('%s.%s');\n" % (self.element.name, css_class))
        code.append("}\n")
        codes.append("".join(code))
        
        for child in self.children:
            code = []
            code.append("%s.prototype.%s = function() {\n" % (js_class, dash_to_camelcase(child.element.get_classes()[0], lower=True)))
            if child.element.kwargs.get("lazy"):
                code.append("    if (this.$%s.length == 0) {\n" % child.get_subselector())
                code.append("        var elem = this.$;\n")
                for element in child.get_subpath():
                    code.append('        elem = $("%s%s").prependTo(elem);\n' % (element.opening_tag(), element.closing_tag()))
                code.append("    }\n")
            code.append("    return new %s(this.$%s.get(0));\n" % (dash_to_camelcase(child.element.get_classes()[0]), child.get_subselector()))
            code.append("}\n")
            codes.append("".join(code))
        
        return codes

