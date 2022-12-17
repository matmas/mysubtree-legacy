class Error(Exception):
    """
    >>> str(Error("aaa"))
    'aaa'
    
    >>> unicode(Error("aaa"))
    u'aaa'
    
    >>> Error("aaa")
    Error('aaa')
    
    >>> Error("aaa") == Error("aaa")
    True
    
    >>> Error("aaa") == Error("bbb")
    False
    """
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __unicode__(self):
        return unicode(self.value)
    
    def __repr__(self):
        return "Error('%s')" % str(self.value)
    
    def __eq__(self, other):
        return self.value == other.value


if __name__ == "__main__":
    import doctest
    doctest.testmod()