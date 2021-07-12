import sys
from importlib import import_module, reload

import requests
from django.conf import settings
from django.urls import clear_url_caches, reverse
from formtools.wizard.views import normalize_name


def create_response(json_body={}, status_code=200, content=None):
    response = requests.Response()
    response.status_code = status_code
    response.json = lambda: json_body
    response._content = content
    return response


def submit_step_factory(client, url_name, view_class):
    step_names = iter([name for name, form in view_class.form_list])
    view_name = normalize_name(view_class.__name__)

    def submit_step(data, step_name=None):
        step_name = step_name or next(step_names)
        return client.post(
            reverse(url_name, kwargs={'step': step_name}),
            {view_name + '-current_step': step_name, **{step_name + '-' + key: value for key, value in data.items()}},
        )

    return submit_step


def reload_urlconf(urlconf=None):
    clear_url_caches()
    if urlconf is None:
        urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])
    else:
        import_module(urlconf)
