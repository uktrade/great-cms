from django.views.generic import TemplateView
from great_components.mixins import GA360Mixin


class IOOMixin:
    def dispatch(self, request, *args, **kwargs):
        # serializer = serializers.ExportPlanSerializer(data={'ui_progress': {self.slug: {'modified': datetime.now()}}})
        # serializer.is_valid()
        # helpers.update_exportplan(
        #     id=self.processor.data['pk'],
        #     sso_session_id=self.request.user.session_id,
        #     data=serializer.data,
        # )
        return super().dispatch(request, *args, **kwargs)

    # @cached_property
    # def processor(self):
    #     export_plan_id = int(self.kwargs['id'])
    #     export_plan = helpers.get_exportplan(self.request.user.session_id, export_plan_id)
    #     return ExportPlanProcessor(export_plan)


class IOOIndex(GA360Mixin, TemplateView):
    def __init__(self):
        super().__init__()
        self.set_ga360_payload(
            page_id='IOOIndex',
            business_unit='IOO',
            site_section='ioo',
        )

    template_name = 'ioo/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # if self.request.user.is_authenticated:
        #     context['exportplan_list'] = helpers.get_exportplan_detail_list(self.request.user.session_id)
        return context
