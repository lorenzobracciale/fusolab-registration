from django import template
from django.template import resolve_variable
from django.contrib.auth.models import Group
from django.template import resolve_variable, NodeList
from bar.models import PriceListDisplay

register = template.Library()

@register.tag()
def ifstockmarket(parser, token):
    """ Check if stock market is running

    Usage: {% ifstockmarket active %} ... {% endifstockmarket %}

    """
    try:
        tokensp = token.split_contents()
        status = tokensp[1]
        if status == 'active':
            status = True
        elif status == 'deactive':
            status = False
        else:
            raise template.TemplateSyntaxError("Tag 'ifstockmarket' requires at least 1 argument that should be active or deactive.")

    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifstockmarket' requires at least 1 argument.")

    nodelist_true = parser.parse(('else', 'endifstockmarket'))
    token = parser.next_token()

    if token.contents == 'else':
        nodelist_false = parser.parse(('endifstockmarket',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()

    return StatusCheckNode(status, nodelist_true, nodelist_false)


class StatusCheckNode(template.Node):
    def __init__(self, status, nodelist_true, nodelist_false):
        self.status = status 
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        pd = PriceListDisplay.objects.get(pk=1)
        if pd.variation_active  == self.status:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)
