from django import template
from datetime import time, datetime

register = template.Library()

@register.filter
def sub(value, arg):
    return value - arg

@register.filter
def filter_useYn(list, use_yn):
    return list.filter(use_yn=use_yn)

@register.filter
def div(value, arg):
    return value / arg

@register.filter
def smart_time(value):
    if not value:
        return ''
    if isinstance(value, (time, datetime)):
        return value.strftime('%H:%M')
    return str(value)