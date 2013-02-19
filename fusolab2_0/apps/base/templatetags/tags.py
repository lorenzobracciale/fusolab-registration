from django import template

register = template.Library()

@register.simple_tag
def active(request, pattern):
    import re
    if pattern == ''  or pattern == '/' : # searching for home
        if request.path == '' or request.path == '/':
            return 'selected' 
    elif re.search(pattern, request.path):
        return 'selected' 
    return ''

