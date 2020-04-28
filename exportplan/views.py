from datetime import datetime
import json

from django.views.generic import TemplateView
from django.utils.functional import cached_property

from directory_constants.choices import INDUSTRIES

from exportplan import data, helpers, serializers
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class BaseExportPlanView(TemplateView):

    @cached_property
    def export_plan(self):
        return helpers.get_or_create_export_plan(self.request.user)

    def get_context_data(self, *args, **kwargs):
        industries = [name for id, name in INDUSTRIES]
        country_choices = [{'value': key, 'label': label} for key, label in helpers.get_madb_country_list()]

        return super().get_context_data(
            next_section=self.next_section,
            sections=data.SECTION_TITLES,
            sectors=json.dumps(industries),
            country_choices=json.dumps(country_choices),
            *args, **kwargs)


class ExportPlanSectionView(BaseExportPlanView):

    @property
    def slug(self, **kwargs):
        return self.kwargs['slug']

    def get_template_names(self, **kwargs):
        return [f'exportplan/sections/{self.slug}.html']

    @property
    def next_section(self):
        if self.slug == data.SECTION_SLUGS[-1]:
            return None

        index = data.SECTION_SLUGS.index(self.slug)
        return {
            'title': data.SECTION_TITLES[index + 1],
            'url': data.SECTION_URLS[index + 1],
        }


class ExportPlanTargetMarketsView(ExportPlanSectionView):
    slug = 'target-markets'
    template_name = 'exportplan/sections/target-markets.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            selected_sectors=json.dumps(self.export_plan.get('sectors', [])),
            target_markets=json.dumps(self.export_plan.get('target_markets', [])),
            datenow=datetime.now(),
        )


class UpdateExportPlanAPIView(generics.GenericAPIView):

    serializer_class = serializers.ExportPlanSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        export_plan = helpers.get_or_create_export_plan(self.request.user)
        helpers.update_exportplan(
            sso_session_id=self.request.user.session_id,
            id=export_plan['pk'],
            data=serializer.validated_data
        )
        return Response({})
