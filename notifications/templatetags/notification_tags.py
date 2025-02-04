from django import template
import re

register = template.Library()


@register.filter
def get_attr(obj, attr):
    """Get attribute from object"""
    return getattr(obj, attr, False)


@register.filter
def split(value, arg):
    """Split a string into a list"""
    return value.split(arg)


@register.filter
def replace(value, arg):
    """Replace underscores with spaces"""
    return value.replace(arg, ' ')
