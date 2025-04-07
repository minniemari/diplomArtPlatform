from django import template

register = template.Library()

# @register.filter
# def get_field(form, field_name):
#     return form[field_name]

@register.filter
def getattribute(obj, attr_name):
    try:
        return getattr(obj, attr_name)
    except AttributeError:
        return None
