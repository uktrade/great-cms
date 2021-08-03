from django.views.generic import TemplateView


class SellingOnlineOverseasView(TemplateView):
    template_name = 'selling-online-overseas.html'

    def get_context_data(self):
        return {'soo_tab_classes': 'active'}
