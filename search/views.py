import datetime
import logging
import urllib

from django.core.paginator import Paginator
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from wagtail.models import Page

from core import helpers as core_helpers
from search import forms

logger = logging.getLogger(__name__)


class OpensearchView(TemplateView):
    """
    This view uses the built-in Wagtail query function to query Opensearch. Returns paginated results.
    """

    MAX_PER_PAGE = 10
    template_name = 'search_opensearch.html'
    page_type = 'SearchResultsPage'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', None)
        full_search_results = Page.objects.none()

        if search_query:
            # Get the full un-paginated listing of search results as a queryset. Live pages only.
            full_search_results = Page.objects.live().search(search_query)
            # Show 10 resources per page
            paginator = Paginator(full_search_results, self.MAX_PER_PAGE)
            page_obj = paginator.get_page(self.request.GET.get('page', 1))
            elided_page_range = [
                page_num
                for page_num in page_obj.paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1)
            ]
            ctx['page_obj'] = page_obj
            ctx['elided_page_range'] = elided_page_range

        ctx['search_results'] = full_search_results
        ctx['search_results_count'] = full_search_results.count()
        ctx['search_query'] = search_query

        return ctx


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
        email = form.cleaned_data['contact_email'] or 'emailnotgiven@example.com'  # /PS-IGNORE
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
