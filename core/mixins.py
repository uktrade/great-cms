class WagtailAdminExclusivePageMixin:
    """
    Limits creation of pages in Wagtail's admin UI to only one instance of a specific type.
    """

    @classmethod
    def can_create_at(cls, parent):
        return super().can_create_at(parent) and not cls.objects.exists()
