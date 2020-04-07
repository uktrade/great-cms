from directory_constants import choices
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db.models import F, Count, IntegerField, ExpressionWrapper
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView

from core import forms, helpers, serializers
from learn.models import TopicPage


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        session_id = self.request.user.session_id
        topics = (
            TopicPage.objects.live()
            .annotate(read_count=Count('read_hits_topic'))
            .annotate(read_progress=(
                ExpressionWrapper(
                    expression=F('read_count') * 100 / F('numchild'),
                    output_field=IntegerField()
                )
            ))
            .order_by('-read_progress')
        )
        return super().get_context_data(
            topics=topics,
            export_plan_progress_form=forms.ExportPlanForm(initial={'step_a': True, 'step_b': True, 'step_c': True}),
            industry_options=[{'value': key, 'label': label} for key, label in choices.SECTORS],
            events=helpers.get_dashboard_events(session_id),
            export_opportunities=helpers.get_dashboard_export_opportunities(session_id, self.request.user.company),
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
    form_class = forms.ArticleForm

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


class ProductLookupView(generics.GenericAPIView):
    serializer_class = serializers.ProductLookupSerializer
    permission_classes = []

    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = helpers.search_commodity_by_term(term=serializer.validated_data['q'])
        return Response(data)
