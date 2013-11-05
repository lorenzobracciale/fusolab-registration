import re

def is_polite(txt):
    """
    Search for profanities
    """
    r = re.compile(r'porco\s?d\w+|madonna|coop|cazzo|culo|stronz|puttana|troia|coglion',  re.IGNORECASE)
    return not r.search(txt)


