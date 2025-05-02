from django import template

register = template.Library()

@register.simple_tag
def create_dict(*args):
    """
    Usage: {% create_dict "key1" "value1" "key2" "value2" as my_dict %}
    Returns a dictionary created from the given key-value pairs.
    """
    if len(args) % 2 != 0:
        raise ValueError("create_dict tag requires an even number of arguments (key-value pairs).")
    
    return {args[i]: args[i + 1] for i in range(0, len(args), 2)}
