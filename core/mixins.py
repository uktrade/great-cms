from django.core.exceptions import ObjectDoesNotExist


class WagtailAdminExclusivePageMixin:
    """
    Limits creation of pages in Wagtail's admin UI to only one instance of a specific type.
    """

    @classmethod
    def can_create_at(cls, parent):
        return super().can_create_at(parent) and not cls.objects.exists()


class ExportTourToTemplateMixin:
    def get_context(self, request):
        context = super().get_context(request)
        try:
            context['tour'] = {
                'title': self.tour.title,
                'body': self.tour.body,
                'button_text': self.tour.button_text,
                'steps': list(self.tour.steps.values('title', 'body', 'position', 'selector'))
            }
        except ObjectDoesNotExist:
            pass
        return context

