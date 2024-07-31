import datetime
import logging
import urllib

from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from requests.exceptions import RequestException

from core import helpers as core_helpers
from search import forms, helpers

logger = logging.getLogger(__name__)


class SearchView(TemplateView):
    """Search results page.

    URL parameters:
        q:string - string to be searched
        page:int - results page number
    """

    template_name = 'search.html'
    page_type = 'SearchResultsPage'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        results = {}
        query = self.request.GET.get('q', '')
        submitted = self.request.GET.get('submitted', '')
        page = helpers.sanitise_page(self.request.GET.get('page', '1'))

        common = {
            'submitted': submitted,
            'query': query,
            'current_page': page,
        }

        try:
            opensearch_query = helpers.format_query(query, page)
            response = helpers.search_with_activitystream(opensearch_query)
        except RequestException:
            logger.error(
                "Activity Stream connection for Search failed. Query: '{query}'".format(
                    query=query,
                )
            )
            results = {
                'error_status_code': 500,
                'error_message': 'Activity Stream connection failed',
            }
        else:
            if response.status_code != 200:
                results = {
                    'error_message': response.content,
                    'error_status_code': response.status_code,
                }

            else:
                results = helpers.parse_results(
                    response,
                    query,
                    page,
                )

        return {**context, **common, **results}


class SearchFeedbackFormView(FormView):
    template_name = 'search_feedback.html'
    form_class = forms.FeedbackForm
    page_type = 'SearchFeedbackPage'

    def get_success_url(self):
        page = self.request.POST['from_search_page']
        query = self.request.POST['from_search_query']
        url = reverse_lazy('search:search')
        if self.request.GET.get('next'):
            return (
                reverse_lazy('search:feedback-success')
                + f'?next={core_helpers.check_url_host_is_safelisted(self.request)}'
            )
        return f'{url}?page={page}&q={query}&submitted=true'

    # email_address and full_name are required by FormsAPI.
    # However, in the UI, the user is given the option
    # to give contact details or not. Therefore defaults
    # are submitted if the user does not want to be contacted
    # to appease FormsAPI.
    #
    def form_valid(self, form):
        email = form.cleaned_data['contact_email'] or 'emailnotgiven@example.com'
        name = form.cleaned_data['contact_name'] or 'Name not given'
        subject = 'Search Feedback - ' + datetime.datetime.now().strftime('%H:%M %d %b %Y')

        response = form.save(
            email_address=email,
            full_name=name,
            subject=subject,
            form_url=self.get_form_url(),
        )
        response.raise_for_status()
        return super().form_valid(form)

    def get_initial(self):
        return {
            'from_search_query': self.request.GET.get('q', ''),
            'from_search_page': self.request.GET.get('page', ''),
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bespoke_breadcrumbs = [
            {'title': 'Search', 'url': reverse('search:search')},
        ]
        context['bespoke_breadcrumbs'] = bespoke_breadcrumbs
        context.update(
            {
                'page': self.request.GET.get('page', ''),
                'q': self.request.GET.get('q', ''),
            }
        )
        return context

    def get_form_url(self):
        # pass through next parameter to forms API
        # search params get passed in request body
        if self.request.GET.get('next'):
            url = self.request.get_full_path()
            return urllib.parse.unquote(url)
        else:
            return self.request.path


class SearchFeedbackSuccessView(TemplateView):
    template_name = 'search_feedback_confirmation.html'

    def get_context_data(self, **kwargs):
        if self.request.GET.get('next'):
            next_url = core_helpers.check_url_host_is_safelisted(self.request)
            return super().get_context_data(**kwargs, next_url=next_url)
        return super().get_context_data(**kwargs)
