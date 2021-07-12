from great_components.middleware import AbstractPrefixUrlMiddleware


class PrefixUrlMiddleware(AbstractPrefixUrlMiddleware):
    prefix = '/profile/'
