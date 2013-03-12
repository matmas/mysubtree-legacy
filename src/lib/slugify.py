import unicodedata
import re

# From tipfy & slightly modified for speed
def slugify(value, max_length=40, default=None):
    """Converts a string to slug format (all lowercase, words separated by
    dashes).

    :param value:
        The string to be slugified.
    :param max_length:
        An integer to restrict the resulting string to this
        maximum length. Words are not broken when restricting length.
    :param default:
        A default value in case the resulting string is empty.
    :returns:
        A slugified string.
    """
    if value is None:
        return None
    if not isinstance(value, unicode):
        value = value.decode('utf8')

    s = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').lower()
    #s = value.encode('translit/long') #TODO: change to this
    s = re.sub('-+', '-', re.sub('[^a-zA-Z0-9-]+', '-', s)).strip('-')
    if not s:
        return default

    if max_length:
        s = s[:max_length+1]

        # Restrict length without breaking words.
        while len(s) > max_length:
            if s.find('-') == -1:
                s = s[:max_length]
            else:
                s = s.rsplit('-', 1)[0]

    return s