import doctest
from pyquery import PyQuery as pq

def preprocess(html):
    """
    >>> html = 'Hello world, <span id="visitor" class="part">visitor</span> <span id="logout" class="part">logout</span>'
    >>> preprocess(html)
    {'visitor': {'start': 13, 'end': 63}, 'logout': {'start': 64, 'end': 110}}
    """
    
    #print "\n".join(dir(pq(html)))
    
    metadata = {}
    pq_html = pq(html)
    print pq_html
    
    for part in pq_html(".part"):
        removed = pq(part).remove()
        print pq_html
        
        
        #print "\n".join(dir(part))
    return {}
    
    part_metadata = {}
    print part
    
    begin = pq(part).begin
    end = pq(part).end
    
    return metadata
    
if __name__ == "__main__":
    doctest.testmod()