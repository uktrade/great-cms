from django.conf import settings
from django.forms.renderers import DjangoTemplates
from django.utils.functional import cached_property


class GDSDivFormRenderer(DjangoTemplates):
    """
    Form renderer to point to the new gds templates
    """

    @cached_property
    def engine(self):
        return self.backend(
            {
                'APP_DIRS': True,
                'DIRS': [
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
                    / 'widgets',
                    settings.ROOT_DIR
                    / 'node_modules'
                    / '@uktrade'
                    / 'great-design-system'
                    / 'dist'
                    / 'components'
                    / 'hint',
                    settings.ROOT_DIR
                    / 'node_modules'
                    / '@uktrade'
                    / 'great-design-system'
                    / 'dist'
                    / 'components'
                    / 'label',
                ],
                'NAME': 'gdsforms',
                'OPTIONS': {},
            }
        )
