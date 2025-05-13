from django import template
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

register = template.Library()

@register.filter(name='urlsafe_base64_encode_filter')
def urlsafe_base64_encode_filter(value):
    return urlsafe_base64_encode(force_bytes(value))
