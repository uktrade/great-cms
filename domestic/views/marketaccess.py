from directory_forms_api_client import actions
from directory_forms_api_client.helpers import Sender
from django.conf import settings
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import TemplateView
from formtools.wizard.views import NamedUrlSessionWizardView

from core import mixins
from domestic.forms import (
    MarketAccessAboutForm,
    MarketAccessProblemDetailsForm,
    MarketAccessSummaryForm,
)


class BespokeBreadcrumbMixin(TemplateView):
    def get_context_data(self, **kwargs):
        bespoke_breadcrumbs = [
            {'title': 'Trade barriers', 'url': reverse('domestic:market-access')},
        ]
        return super().get_context_data(bespoke_breadcrumbs=bespoke_breadcrumbs, **kwargs)


class MarketAccessView(
    mixins.MarketAccessFeatureFlagMixin,
    BespokeBreadcrumbMixin,
    TemplateView,
):
    template_name = 'domestic/marketaccess/report_a_barrier.html'


class ReportMarketAccessBarrierSuccessView(
    BespokeBreadcrumbMixin,
    mixins.MarketAccessFeatureFlagMixin,
    TemplateView,
):
    template_name = 'domestic/marketaccess/report_barrier_form/success.html'


class ReportMarketAccessBarrierFormView(
    BespokeBreadcrumbMixin,
    mixins.MarketAccessFeatureFlagMixin,
    NamedUrlSessionWizardView,
):
    ABOUT = 'about'
    PROBLEM_DETAILS = 'problem-details'
    SUMMARY = 'summary'
    FINISHED = 'finished'

    form_list = (
        (ABOUT, MarketAccessAboutForm),
        (PROBLEM_DETAILS, MarketAccessProblemDetailsForm),
        (SUMMARY, MarketAccessSummaryForm),
    )

    templates = {
        ABOUT: 'domestic/marketaccess/report_barrier_form/step-about.html',
        PROBLEM_DETAILS: 'domestic/marketaccess/report_barrier_form/step-problem.html',
        SUMMARY: 'domestic/marketaccess/report_barrier_form/step-summary.html',
        FINISHED: 'domestic/marketaccess/report_barrier_form/success.html',
    }

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == self.SUMMARY:
            data = self.get_all_cleaned_data()
            context['all_cleaned_data'] = data
        if form.errors:
            for field in form:
                context['formatted_form_errors'] = render_to_string(
                    'domestic/marketaccess/report_barrier_form/error-link-list.html', {'form': form}
                )
        return context

    def serialize_form_list(self, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        return data

    def done(self, form_list, form_dict, **kwargs):
        data = self.serialize_form_list(form_list)
        subject = f"{settings.MARKET_ACCESS_ZENDESK_SUBJECT}: {data['location']}: {data['company_name']}"
        sender = Sender(email_address=data['email'], country_code=None)
        action = actions.ZendeskAction(
            email_address=data['email'],
            full_name=f"{data['firstname']} {data['lastname']}",
            subject=subject,
            service_name=settings.MARKET_ACCESS_FORMS_API_ZENDESK_SERVICE_NAME,
            subdomain=settings.EU_EXIT_ZENDESK_SUBDOMAIN,
            form_url=reverse(
                'domestic:report-ma-barrier',
                kwargs={'step': 'about'},
            ),
            sender=sender,
        )
        response = action.save(data)
        response.raise_for_status()

        context = {
            'all_cleaned_data': self.get_all_cleaned_data(),
        }
        return TemplateResponse(
            self.request,
            self.templates['finished'],
            context,
        )
