import re


def dash_to_camelcase(value, lower=False):
    def camelcase(str):
        yield str.lower if lower else str.capitalize # first word
        while True:
            yield str.capitalize
    c = camelcase(type(value))
    return "".join(c.next()(x) if x else '-' for x in value.split("-"))


#http://stackoverflow.com/a/1176023
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def decamelcase(name, separator):
    s1 = first_cap_re.sub(r'\1%s\2' % separator, name)
    return all_cap_re.sub(r'\1%s\2'% separator, s1).lower()
