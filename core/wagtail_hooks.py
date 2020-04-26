from wagtail.core import hooks

from django.http import HttpResponseRedirect

from core import mixins


@hooks.register('before_serve_page')
def anonymous_user_required(page, request, serve_args, serve_kwargs):
    if isinstance(page, mixins.AnonymousUserRequired):
        if request.user.is_authenticated:
            return HttpResponseRedirect(page.anonymous_user_required_redirect_url)
