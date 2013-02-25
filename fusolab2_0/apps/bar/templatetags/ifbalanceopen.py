from django import template
from django.template import resolve_variable, NodeList
from datetime import datetime
from bar.models import *
from ingresso.models import EntranceBalance

register = template.Library()

@register.tag()
def ifbalanceopen(parser, token):
    """
    Check if the current balance is open (must specify the balance type)
    """
    try:
        tag, balance_type = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifbalanceopen' requires 1 argument.")

    if balance_type not in ('bar', 'ingresso'):
        raise template.TemplateSyntaxError("Tag 'ifbalanceopen' requires bar or ingresso parameters.")
    
    nodelist_true = parser.parse(('else', 'endifbalanceopen'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifbalanceopen',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return BalanceCheckNode(balance_type, nodelist_true, nodelist_false)


class BalanceCheckNode(template.Node):
    def __init__(self, balance_type, nodelist_true, nodelist_false):
        self.balance_type = balance_type
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        user = resolve_variable('user', context)
        
        if not user.is_authenticated():
            return self.nodelist_false.render(context)
          
        if self.balance_type == "ingresso": 
            if EntranceBalance.objects.is_open(datetime.now()):
                return self.nodelist_true.render(context)  
            else:
                return self.nodelist_false.render(context)
        elif self.balance_type == "bar":
            if BarBalance.objects.is_open(datetime.now()):
                return self.nodelist_true.render(context)  
            else:
                return self.nodelist_false.render(context)
