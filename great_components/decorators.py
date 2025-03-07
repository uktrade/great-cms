from functools import wraps


def skip_ga360(view_function):

    @wraps(view_function)
    def _wrapped_view_function(request, *args, **kwargs):
        response = view_function(request, *args, **kwargs)
        response.skip_ga360 = True
        return response

    return _wrapped_view_function
