from django.db import models


class NonPageContentSnippetBase(models.Model):
    # Ensures all ContentSnippets have the minimum reqired fields, such as `slug`
    class Meta:
        abstract = True

    slug_options = {
        # Override this in subclasses with the following spec
        # {
        #     'some-slug-ideally-from-shared-constants': {
        #         'title': 'internal title string here',
        #         ... additional key-value pairs as you need
        #     },
        # },
        # {
        #     ... more options as required
        # },
        # ...
    }

    slug = models.CharField(
        choices=[(key, val['title']) for key, val in slug_options.items()],
        max_length=255,
        unique=True,
        verbose_name='Purpose',
        help_text='Select the use-case for this snippet from a fixed list of choices',
    )

    internal_title = models.CharField(
        max_length=255,
        verbose_name='Title (internal use only - not publicly shown)',
        editable=False,
    )

    def save(self, *args, **kwargs):
        if not self.slug_options:
            raise NotImplementedError('The subclass must have slug_options defined.')

        if not self.slug:
            raise NotImplementedError('The subclass must set a value for self.slug before during save()')

        field_values = self.slug_options.get(self.slug, {})
        self.internal_title = field_values.get('title')
        return super().save(*args, **kwargs)


class NonPageContentSEOMixin(models.Model):
    """Provides the SEO panels/fields that pages usually have, but for Snippets that
    are used to provide editable content chunks slotted inot Django views/wizards"""

    class Meta:
        abstract = True

    seo_title = models.CharField(
        max_length=255,
        verbose_name='Page title',
        help_text="Optional. 'Search Engine Friendly' title. This will appear at the top of the browser window.",
        blank=True,
    )

    search_description = models.TextField(
        verbose_name='Search description',
        blank=True,
    )
