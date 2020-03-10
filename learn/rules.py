from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail_personalisation.rules import AbstractBaseRule


class MatchProductQuerystring(AbstractBaseRule):
    """Match product in the querystring"""
    icon = 'fa-user'

    product = models.ForeignKey('core.Product', on_delete=models.CASCADE)

    panels = [
        FieldPanel('product'),
    ]

    class Meta:
        verbose_name = 'Match product rule'

    def test_user(self, request=None):
        return request.GET.get('product') == self.product.name

    def description(self):
        return {
            'title': 'Match this product in querystring:',
            'value': f'{self.product.name}',
            'code': True
        }


class MatchCountryQuerystring(AbstractBaseRule):
    """Match country in querystring"""
    icon = 'fa-user'

    country = models.ForeignKey('core.Country', on_delete=models.CASCADE)

    panels = [
        FieldPanel('country'),
    ]

    class Meta:
        verbose_name = 'Match country rule'

    def test_user(self, request=None):
        return request.GET.get('country') == self.country.name

    def description(self):
        return {
            'title': 'Match this country in querystring',
            'value': f'{self.country.name}',
            'code': True
        }
