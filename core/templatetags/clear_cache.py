from django import template
from django.core.cache import cache
from urllib.parse import quote
from hashlib import md5

register = template.Library()


class ClearCacheNode(template.Node):
    def __init__(self, fragment_name, vary_on):
        self.fragment_name = fragment_name
        self.vary_on = vary_on

    def render(self, context):
        # Build a unicode key for this fragment and all vary-on's.
        args = md5(
            u':'.join([quote(template.Variable('request').resolve(var, context)) for var in self.vary_on]).encode(
                'utf-8'
            )
        )
        from django.core.cache.utils import make_template_fragment_key

        cache_key = 'template.cache.%s.%s' % (self.fragment_name, args.hexdigest())
        print('clear-cache key', cache_key)
        from django.core.cache import cache

        key = make_template_fragment_key('hcsat')

        result2 = cache.delete(key)
        result1 = cache.delete_many(keys=cache.keys('*hcsat*'))
        result = cache.delete(cache_key)
        print('result', result)
        print('result1', result1)
        print('result2', result2)
        return ''


@register.simple_tag
def clear_cache(parser, token):
    """
    This will clear the cache for a template fragment

    Usage::

        {% load clearcache %}
        {% clearcache [fragment_name] %}

    This tag also supports varying by a list of arguments::

        {% load clearcache %}
        {% clearcache [fragment_name] [var1] [var2] .. %}

    The set of arguments must be the same as the original cache tag (except for expire_time).
    """
    try:
        tokens = token.split_contents()
        print('tokens', tokens)
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires at least one argument' % token.contents.split()[0])
    return ClearCacheNode(tokens[1], tokens[2:])


register.tag('clear_cache', clear_cache)
