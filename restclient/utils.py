import re


def reverse(pattern, **kwargs):
    template = pattern.strip('^$')

    start = re.compile(r'\(\?P\<')
    end = re.compile(r'\>[^\)]*\)')
    
    template = start.sub('%(', template)
    template = end.sub(')s', template)
    
    try:
        result = template % kwargs
    except KeyError, e:
        raise ValueError('The URL pattern requires %s as named argument.' % e)
    
    return result
