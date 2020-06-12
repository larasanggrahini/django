from django import template
from ..models import Reference
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.inclusion_tag('reference/post/latest_reference.html')
def show_latest_reference(count=5):
    latest_reference = Reference.getReference.order_by('-created')[:count]
    return {'latest_reference': latest_reference}

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text)) #return safe string html