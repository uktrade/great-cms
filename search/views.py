import datetime
import logging
import urllib

import sentry_sdk
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from requests.exceptions import RequestException
from wagtail.models import Page

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
                sentry_sdk.capture_message(
                    f'/search failed: status code {response.status_code}, message: {response.content}', 'error'
                )
            else:
                results = helpers.parse_results(
                    response,
                    query,
                    page,
                )
        return {**context, **common, **results}


class OpensearchView(TemplateView):
    """
    This view uses the built-in Wagtail query function to query Opensearch. Returns paginated results.
    """

    template_name = 'search_opensearch.html'
    page_type = 'SearchResultsPage'

    def get_context_data(self, *args, **kwargs):
        # Get the search query & page
        search_query = self.request.GET.get('q', None)
        page = self.request.GET.get('page', 1)
        show_first_page = False
        show_last_page = False
        prev_pages = None
        next_pages = None
        total_pages = 0

        if search_query:
            # Get the full un-paginated listing of search results as a queryset. Live pages only.
            full_search_results = Page.objects.live().search(search_query)
            # Show 10 resources per page
            paginator = Paginator(full_search_results, 10)
            total_pages = len(paginator.page_range)
            # Paginate
            try:
                paginated_search_results = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                paginated_search_results = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                paginated_search_results = paginator.page(paginator.num_pages)

            # Trunctated Pagination logic
            prev_pages = list(range(1, int(page)))[-3:]
            if (len(prev_pages) > 0) and (prev_pages[0] > 2):
                show_first_page = True

            next_pages = list(range(int(page) + 1, total_pages + 1))[:3]
            if (len(next_pages) > 0) and (next_pages[-1] + 1 < total_pages):
                show_last_page = True

        else:
            # No search query provided
            full_search_results = Page.objects.none()
            paginated_search_results = Page.objects.none()

        return {
            'search_query': search_query,
            'search_results': paginated_search_results,
            'search_results_count': len(full_search_results),
            'current_page': page,
            'total_pages': total_pages,
            'show_first_page': show_first_page,
            'show_last_page': show_last_page,
            'prev_pages': prev_pages,
            'next_pages': next_pages,
        }


class OpensearchAdminView(TemplateView):
    """
    This view is an admin preview of Opensearch on servers where it is not deployed yet.
    """

    template_name = 'search_preview_opensearch.html'
    page_type = 'SearchResultsPage'

    def get_context_data(self, *args, **kwargs):
        # Get the search query & page
        search_query = self.request.GET.get('q', None)
        page = self.request.GET.get('page', None)

        if search_query:
            # Get the full un-paginated listing of search results as a queryset. Live pages only.
            full_search_results = Page.objects.live().search(search_query)
            # Show 10 resources per page
            paginator = Paginator(full_search_results, 10)
            # Paginate
            try:
                paginated_search_results = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                paginated_search_results = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                paginated_search_results = paginator.page(paginator.num_pages)
        else:
            # No search query provided
            full_search_results = Page.objects.none()
            paginated_search_results = Page.objects.none()

        return {
            'search_query': search_query,
            'search_results': paginated_search_results,
            'search_results_count': len(full_search_results),
        }


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


class GDSSearchFeedbackFormView(SearchFeedbackFormView):
    template_name = 'gds_search_feedback.html'
    form_class = forms.GDSFeedbackForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # form = context["form"]
        # for field in form.fields.values():
        #     try:
        #         print (field.widget.field.gds_mapping)
        #     except AttributeError:
        #         print('missing')

        return context


class SearchFeedbackSuccessView(TemplateView):
    template_name = 'search_feedback_confirmation.html'

    def get_context_data(self, **kwargs):
        if self.request.GET.get('next'):
            next_url = core_helpers.check_url_host_is_safelisted(self.request)
            return super().get_context_data(**kwargs, next_url=next_url)
        return super().get_context_data(**kwargs)
