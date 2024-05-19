from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    return value * arg

@register.filter
def filter_useYn(list, use_yn):
    return list.filter(use_yn=use_yn)

@register.filter
def div(value, arg):
    return value / arg