import string

MAX_LENGTH = 5

ABBR_TO_SORT = {
    "n": "newest",
    "a": "activity",
    "h": "1hour",
    "d": "1day",
    "w": "1week",
    "m": "1month",
    "y": "1year",
    "v": "alltime",
}

SORT_TO_ABBR = dict((v, k) for k, v in ABBR_TO_SORT.iteritems())

def parse_o(string, max_length=MAX_LENGTH):
    """
    >>> parse_o("")
    []
    
    >>> parse_o(None)
    []
    
    >>> parse_o("n")
    [{'sort': 'newest'}]
    
    >>> parse_o("nn")
    [{'sort': 'newest'}, {'sort': 'newest'}]
    
    >>> parse_o("n10n")
    [{'sort': 'newest', 'offset': 10}, {'sort': 'newest'}]
    
    >>> parse_o("nn10")
    [{'sort': 'newest'}, {'sort': 'newest', 'offset': 10}]
    
    >>> parse_o("10nn")
    [{'sort': 'newest'}, {'sort': 'newest'}]
    
    >>> parse_o("nnnnn")
    [{'sort': 'newest'}, {'sort': 'newest'}, {'sort': 'newest'}, {'sort': 'newest'}, {'sort': 'newest'}]
    
    >>> parse_o("nnnnna")
    [{'sort': 'newest'}, {'sort': 'newest'}, {'sort': 'newest'}, {'sort': 'newest'}, {'sort': 'newest'}]
    """
    state = []
    last_nondigit_pos = -1
    if string:
        string += "\n"
        for i, c in enumerate(string):
            if not c.isdigit():
                o = string[last_nondigit_pos + 1:i]
                if o and state:
                    state[-1]["offset"] = int(o)
                
                sort = ABBR_TO_SORT.get(c)
                if sort:
                    settings = {"sort": sort}
                    if len(state) == max_length:
                        break
                    state.append(settings)
                
                last_nondigit_pos = i
    return state


_default_sort = "newest"
_default_offset = 0


def get_sort(viewstate, viewlevel):
    return viewstate[viewlevel].get("sort", _default_sort)

def get_offset(viewstate, viewlevel):
    return viewstate[viewlevel].get("offset", _default_offset)


def compile_o(viewstate, max_length=MAX_LENGTH):
    """
    >>> compile_o(parse_o("nnn"))
    'nnn'
    
    >>> compile_o(parse_o("nnn0"))
    'nnn'
    
    >>> compile_o(parse_o("nn10n"))
    'nn10n'
    
    >>> compile_o(parse_o("nnnnn"))
    'nnnnn'
    
    >>> compile_o(parse_o("nnnnna"))
    'nnnnn'
    """
    parts = []
    for branch in list(viewstate)[:max_length]:
        sort = branch.get("sort", _default_sort)
        s = SORT_TO_ABBR[sort]
        offset = branch.get("offset", _default_offset)
        
        if offset != _default_offset:
            part = s + str(offset)
        else:
            part = s
        
        parts.append(part)
    return "".join(parts)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
