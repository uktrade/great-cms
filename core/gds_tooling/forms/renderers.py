from django.forms.renderers import DjangoTemplates
from django.utils.functional import cached_property
from django.conf import settings


class GDSDivFormRenderer(DjangoTemplates):
    """
    Form renderer to point to the new gds templates
    """

    # New gds template
    form_template_name = "_div.html"
    formset_template_name = "django/forms/formsets/div.html"

    @cached_property
    def engine(self):
        return self.backend(
            {
                "APP_DIRS": True,
                "DIRS": [
                    settings.ROOT_DIR
                    / 'node_modules'
                    / '@uktrade'
                    / 'great-design-system'
                    / 'dist'
                    / 'components'
                    / 'forms',
                    settings.ROOT_DIR
                    / 'node_modules'
                    / '@uktrade'
                    / 'great-design-system'
                    / 'dist'
                    / 'components'
                    / 'forms'
                    / 'widgets',
                    settings.ROOT_DIR
                    / 'node_modules'
                    / '@uktrade'
                    / 'great-design-system'
                    / 'dist'
                    / 'components'
                    / 'forms'
                    / 'legacy',
                ],
                "NAME": "gdsforms",
                "OPTIONS": {},
            }
        )
