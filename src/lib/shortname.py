# -*- coding: utf-8 -*-
def short_name(name, max_length=30, word_separator=" ", append_ellipsis=True):
    s = name
    if len(s) > max_length:
        s = s[:max_length + 1]
        if s.find(word_separator) == -1:
            s = s[:max_length]
        else:
            s = s.rsplit(word_separator, 1)[0]
        if append_ellipsis:
            s += u"…"
    return s