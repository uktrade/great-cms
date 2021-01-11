from django.views.generic import TemplateView

from django.template.response import TemplateResponse


class RobotsView(TemplateView):
    template_name = 'robots.txt'
    content_type = 'text/plain'


def handler404(request, *args, **kwargs):
    return TemplateResponse(
        request=request,
        template='404.html',
        context={},
        status=404
    )


def handler500(request, *args, **kwargs):
    return TemplateResponse(
        request=request,
        template='500.html',
        context={},
        status=500
    )
