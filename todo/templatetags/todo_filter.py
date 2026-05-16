from django import template
from django.utils import timezone
from datetime import timedelta

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

@register.filter
def is_new(value):
    if not value:
        return False
    return value >= timezone.now() - timedelta(days=5)