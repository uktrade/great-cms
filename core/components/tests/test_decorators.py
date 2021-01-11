from django.http import HttpRequest, HttpResponse

from directory_components.decorators import skip_ga360


@skip_ga360
def get_response(request, *args, **kwargs):
    return HttpResponse()


def test_skip_360_adds_attribute_to_response():
    request = HttpRequest()
    get_response(request)

    assert request.skip_ga360 is True
