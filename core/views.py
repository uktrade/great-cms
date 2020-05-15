import abc

from directory_constants import choices
from formtools.wizard.views import NamedUrlSessionWizardView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import F, Q, Count, IntegerField, ExpressionWrapper
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from core import forms, helpers, models, serializers


STEP_START = 'start'
STEP_WHAT_SELLING = 'what-are-you-selling'
STEP_PRODUCT_SEARCH = 'product-search'
STEP_SIGN_UP = 'sign-up'
STEP_COMPANY_NAME = 'company-name'


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        # coerce to list to make the db read happen here rather than in the template, thus making a
        # traceback more debuggable
        list_pages = list(
            models.ListPage.objects.live().filter(record_read_progress=True)
            .annotate(read_count=Count('page_views_list', filter=Q(page_views_list__sso_id=user.id)))
            .annotate(read_progress=(
                ExpressionWrapper(
                    expression=F('read_count') * 100 / F('numchild'),
                    output_field=IntegerField()
                )
            ))
            .order_by('-read_progress')
        )

        return super().get_context_data(
            list_pages=list_pages,
            export_plan_progress_form=forms.ExportPlanForm(initial={'step_a': True, 'step_b': True, 'step_c': True}),
            industry_options=[{'value': key, 'label': label} for key, label in choices.SECTORS],
            events=helpers.get_dashboard_events(user.session_id),
            export_opportunities=helpers.get_dashboard_export_opportunities(user.session_id, user.company),
            **kwargs,
        )


class UpdateCompanyAPIView(generics.GenericAPIView):

    serializer_class = serializers.CompanySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = {key: value for key, value in serializer.validated_data.items() if value}
        if not self.request.user.company:
            data['name'] = f'unnamed sso-{self.request.user.id} company'
        helpers.update_company_profile(sso_session_id=self.request.user.session_id, data=data)
        return Response(status=200)


class ArticleView(FormView):
    template_name = 'core/article.html'
    success_url = reverse_lazy('core:dashboard')
    form_class = forms.NoOperationForm

    def get_context_data(self):
        return super().get_context_data(
            topic_name=self.kwargs['topic'],
            chapter_name=self.kwargs['chapter'],
            article_name=self.kwargs['article'],
            country_choices=[{'value': key, 'label': label} for key, label in choices.COUNTRY_CHOICES],
        )


class LoginView(TemplateView):
    template_name = 'core/login.html'


class SignupView(TemplateView):
    template_name = 'core/signup.html'


class MarketsView(TemplateView):
    template_name = 'core/markets.html'

    def get_page_title(self):
        if self.request.user.is_authenticated:
            return helpers.get_markets_page_title(self.request.user.company)

    def get_most_popular_countries(self):
        if self.request.user.is_authenticated and self.request.user.company.expertise_industries_labels:
            return helpers.get_popular_export_destinations(self.request.user.company.expertise_industries_labels[0])

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            page_title=self.get_page_title(),
            most_popular_countries=self.get_most_popular_countries(),
            **kwargs
        )


class ProductLookupView(generics.GenericAPIView):
    serializer_class = serializers.ProductLookupSerializer
    permission_classes = []

    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = helpers.search_commodity_by_term(term=serializer.validated_data['q'])
        return Response(data)


def handler404(request, *args, **kwargs):
    return TemplateResponse(
        request=request,
        template='core/404.html',
        context={},
        status=404
    )


def handler500(request, *args, **kwargs):
    return TemplateResponse(
        request=request,
        template='core/500.html',
        context={},
        status=500
    )


class AbstractSignupWizardView(abc.ABC):

    step_labels = (
        'Get tailored content',
        'What are you selling?',
        'Find your product',
        'Sign up',
    )

    @property
    @abc.abstractmethod
    def templates(self):
        return {}

    @property
    @abc.abstractmethod
    def form_list(self):
        return []


    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def done(self, form_list, **kwargs):
        # react component handles the signing up, this wizard is just for data collection that is fed into
        # the react component on the final step, so this step should not be submitted to
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(step_labels=self.step_labels, **kwargs)
        if self.steps.current == STEP_SIGN_UP:
            context['product_search_data'] = self.get_cleaned_data_for_step(STEP_PRODUCT_SEARCH)
        return context

    def get_step_url(self, step):
        # we want to maintain the querystring params. e.g, next tells the final
        # step where to send the user
        url = super().get_step_url(step)
        if self.request.GET.get('next'):
            querystring = self.request.META['QUERY_STRING']
            if querystring:
                url = f'{url}?{querystring}'
        return url


class SignupForTailoredContentWizardView(AbstractSignupWizardView, NamedUrlSessionWizardView):
    templates = {
        STEP_START: 'core/signup-wizard-step-start-tailored-content.html',
        STEP_WHAT_SELLING: 'core/signup-wizard-step-what-selling.html',
        STEP_PRODUCT_SEARCH: 'core/signup-wizard-step-product-search.html',
        STEP_SIGN_UP: 'core/signup-wizard-step-sign-up.html',
    }

    form_list = (
        (STEP_START, forms.NoOperationForm),
        (STEP_WHAT_SELLING, forms.WhatAreYouSellingForm),
        (STEP_PRODUCT_SEARCH, forms.ProductSearchForm),
        (STEP_SIGN_UP, forms.NoOperationForm),
    )


class SignupForExportPlanWizardView(AbstractSignupWizardView, NamedUrlSessionWizardView):
    templates = {
        STEP_START: 'core/signup-wizard-step-start-export-plan.html',
        STEP_WHAT_SELLING: 'core/signup-wizard-step-what-selling.html',
        STEP_PRODUCT_SEARCH: 'core/signup-wizard-step-product-search.html',
        STEP_SIGN_UP: 'core/signup-wizard-step-sign-up.html',
        STEP_COMPANY_NAME: 'core/signup-wizard-step-company-name.html',
    }

    form_list = (
        (STEP_START, forms.NoOperationForm),
        (STEP_WHAT_SELLING, forms.WhatAreYouSellingForm),
        (STEP_PRODUCT_SEARCH, forms.ProductSearchForm),
        (STEP_SIGN_UP, forms.NoOperationForm),
        (STEP_COMPANY_NAME, forms.CompanyNameForm),
    )
