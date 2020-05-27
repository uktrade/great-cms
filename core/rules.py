from directory_constants import choices

from wagtail.admin.edit_handlers import FieldPanel
from wagtail_personalisation.rules import AbstractBaseRule

from django.db import models


class MatchProductExpertise(AbstractBaseRule):
    """Match product in the user's expertise"""
    icon = 'fa-user'

    product = models.ForeignKey('core.Product', on_delete=models.CASCADE)

    panels = [
        FieldPanel('product'),
    ]

    class Meta:
        verbose_name = 'Match product rule'

    def test_user(self, request=None):
        if request:
            if request.GET.getlist('product'):
                return self.product.name in request.GET.getlist('product')
            elif request.user.is_authenticated and request.user.company:
                return self.product.name in request.user.company.expertise_products_services

    def description(self):
        return {
            'title': 'Match this product against user expertise:',
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


class MatchFirstCountryOfInterestRule(AbstractBaseRule):
    """Match with first country in user's list of selected countries of interest"""
    icon = 'fa-user'

    country = models.ForeignKey('core.Country', on_delete=models.CASCADE)

    panels = [
        FieldPanel('country'),
    ]

    class Meta:
        verbose_name = 'Match first country of interest rule'

    def test_user(self, request=None):
        user = request.user
        if user.is_authenticated and user.company and user.company.expertise_countries_labels:
            return user.company.expertise_countries_labels[0] == self.country.name
        return False

    def description(self):
        return {
            'title': 'Match this country with chosen country of interest',
            'value': f'{self.country.name}',
            'code': True
        }


class MatchFirstIndustryOfInterestRule(AbstractBaseRule):
    """Match with first industry in user's list of selected countries of interest"""
    icon = 'fa-user'

    industry = models.TextField(choices=choices.SECTORS)

    panels = [
        FieldPanel('industry'),
    ]

    class Meta:
        verbose_name = 'Match first industry of interest rule'

    def test_user(self, request=None):
        user = request.user
        if user.is_authenticated and user.company and user.company.data['expertise_industries']:
            return user.company.data['expertise_industries'][0] == self.industry
        return False

    def description(self):
        return {
            'title': 'Match this country with chosen country of interest',
            'value': f'{self.industry}',
            'code': True
        }
