from django.db import models


class NonPageContentSnippetBase(models.Model):
    # Ensures all ContentSnippets have the minimum reqired fields, such as `slug`
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not hasattr(self, 'slug'):
            raise NotImplementedError('The subclass must have a slug field.')

        if not self.slug:
            raise NotImplementedError('The subclass must set a value for self.slug before during save()')

        return super().save()


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
