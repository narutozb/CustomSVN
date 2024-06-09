from django import template

register = template.Library()


@register.filter
def endswith(value, arg):
    """检查值是否以arg结束"""
    return str(value).endswith(str(arg))


@register.filter
def startswith(value, arg):
    return str(value).startswith(str(arg))
