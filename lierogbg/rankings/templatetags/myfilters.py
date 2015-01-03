"""
Special filters
"""
from django import template

register = template.Library()

@register.filter(name='addcss')
def addcss(value, arg):
    """
    Adds a CSS class to the specified widget
    """
    # FIXME rename to add_class
    return value.as_widget(attrs={'class': arg})

