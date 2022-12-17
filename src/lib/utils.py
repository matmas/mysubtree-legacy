# -*- coding: utf-8 -*-
from flask import Markup
from difflib import SequenceMatcher
from diff_match_patch import diff_match_patch

from .shortname import short_name
from .slugify import slugify


def random_word(length):
    """
    Returns random alphanumeric string of length word_length.
    >>> len(random_word(5))
    5
    >>> random_word(20) == random_word(20)
    False
    """
    import random
    import string
    return "".join(
        random.choice(string.letters + string.digits) for i in xrange(length)
    )

    #import random
    #import string
    #self._id = "".join(random.sample(string.letters, 10))
    

def get_diff(old_text, new_text):
    output = []
    dmp = diff_match_patch()
    diff = dmp.diff_main(old_text, new_text)
    dmp.diff_cleanupSemantic(diff)
    for tag, text in diff:
        if tag == 0: # equal
            output.append(text)
        elif tag == 1: # insert
            output.append("<ins>%s</ins>" % text)
        elif tag == -1: # delete
            output.append("<del>%s</del>" % text)
    return "".join(output)
    
    # This is buggy:
    #old = old_text.split(" ")
    #new = new_text.split(" ")
    #s = SequenceMatcher(lambda whitespace: whitespace == " \t", old, new)
    #diff = []
    #for tag, o1, o2, n1, n2 in s.get_opcodes():
        #if tag == "equal":
            #diff.append("%s" % " ".join(old[n1:n2]))
        #if tag == "insert":
            #diff.append('<ins>%s</ins>' % " ".join(new[n1:n2]))
        #if tag == "delete":
            #diff.append('<del>%s</del>' % " ".join(old[o1:o2]))
        #if tag == "replace":
            #diff.append('<del>%s</del><ins>%s</ins>' % (" ".join(old[o1:o2]), " ".join(new[n1:n2])))
    #return " ".join(diff)


def get_html_diff(old_text, new_text):
    """
    >>> get_html_diff("version1", "version2")
    '<del>version1</del><ins>version2</ins>'
    >>> get_html_diff("version1", "")
    '<del>version1</del>'
    >>> get_html_diff("", "version2")
    '<ins>version2</ins>'
    >>> get_html_diff("version1 version1", "version1")
    'version1<del> version1</del>'
    >>> get_html_diff("version1", "version1 version1")
    'version1<ins> version1</ins>'
    """
    old = old_text.split(" ")
    new = new_text.split(" ")
    s = SequenceMatcher(lambda whitespace: whitespace in " \t\r\n", old, new)
    diff = ""
    for tag, o1, o2, n1, n2 in s.get_opcodes():
        if tag == "equal":
            diff = diff + "%s " % " ".join(old[n1:n2])
        if tag == "insert":
            diff = diff + '<ins>%s</ins> ' % " ".join(new[n1:n2])
        if tag == "delete":
            diff = diff + '<del>%s</del> ' % " ".join(old[o1:o2])
        if tag == "replace":
            diff = diff + '<del>%s</del><ins>%s</ins> ' % (" ".join(old[o1:o2]), " ".join(new[n1:n2]))
    return diff[:-1]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    

#def print_timing(func):
#    import time
#    def wrapper(*arg):
#        t1 = time.time()
#        res = func(*arg)
#        t2 = time.time()
#        print '%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
#        return res
#    return wrapper


#template_lookup = None
#def render_template(template_name, **kwargs):
    #global template_lookup
    #if template_lookup is None:
        #from mako.lookup import TemplateLookup
        #template_lookup = TemplateLookup(directories=".", filesystem_checks=is_development(), output_encoding='utf-8')
    #try:
        #template = template_lookup.get_template("templates/" + template_name)
        #return template.render(**kwargs)
    #except:
        #from mako import exceptions
        #print exceptions.html_error_template().render()