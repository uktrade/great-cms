from directory_constants import choices
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from core import forms, helpers, permissions, serializers


class LandingPageView(TemplateView):
    template_name = 'domestic/domestic_home_page.html'


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            export_plan_progress_form=forms.ExportPlanForm(initial={'step_a': True, 'step_b': True, 'step_c': True}),
            industry_options=[{'value': key, 'label': label} for key, label in choices.SECTORS],
            events=helpers.get_dashboard_events(self.request.user.company),
            export_opportunities=helpers.get_dashboard_export_opportunities(self.request.user.company),
            **kwargs,
        )


class EnrolCompanyAPIView(generics.GenericAPIView):

    serializer_class = serializers.CompanySerializer
    permission_classes = [IsAuthenticated, permissions.HasNoCompany]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        company_data = {
            'sso_id': self.request.user.id,
            'company_email': self.request.user.email,
            'contact_email_address': self.request.user.email,
            'company_name': self.request.data.get('company_name', '<unknown>'),
            'expertise_industries': self.request.data['expertise_industries'],
            'expertise_countries': self.request.data.get('expertise_countries', {}),
        }
        helpers.create_company_profile(company_data)
        if 'first_name' in self.request.data:
            user_data = {
                'first_name': self.request.data['first_name'],
                'last_name': self.request.data['last_name'],
            }
            helpers.create_user_profile(data=user_data, sso_session_id=self.request.user.session_id)
        return Response(status=200)


class UpdateCompanyAPIView(generics.GenericAPIView):

    serializer_class = serializers.CompanySerializer
    permission_classes = [IsAuthenticated, permissions.HasCompany]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        helpers.update_company_profile(sso_session_id=self.request.user.session_id, data=serializer.data)
        return Response(status=200)


class ArticleView(FormView):
    template_name = 'core/article.html'
    success_url = reverse_lazy('core:dashboard')
    form_class = forms.ArticleForm

    def form_valid(self, form):
        # TODO: store the fact the article was viewed
        return super().form_valid(form)

    def get_context_data(self):
        return super().get_context_data(
            topic_name=self.kwargs['topic'],
            chapter_name=self.kwargs['chapter'],
            article_name=self.kwargs['article'],
            country_choices=[{'value': key, 'label': label} for key, label in choices.COUNTRY_CHOICES],
        )


class LoginView(TemplateView):
    template_name = 'core/login.html'


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
