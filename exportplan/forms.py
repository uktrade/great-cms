from great_components import forms
from django.forms import ImageField, Textarea

import directory_validators.url
import directory_validators.string
import directory_validators.file

from core.helpers import population_age_range_choices


class LogoForm(forms.Form):
    logo = ImageField(
        help_text=(
            'For best results this should be a transparent PNG file of 600 x '
            '600 pixels and no more than 2MB',
        ),
        required=True,
        validators=[directory_validators.file.logo_filesize, directory_validators.file.image_format]
    )


class CountryDemographicsForm(forms.Form):
    COUNTRY_CHOICES = [
        'Australia',
        'Brazil',
        'China',
        'France',
        'Germany',
        'India',
        'United States',
    ]

    name = forms.ChoiceField(
        label='Country name',
        choices=((i, i) for i in COUNTRY_CHOICES)
    )
    age_range = forms.ChoiceField(
        choices=((i, i) for i in population_age_range_choices)
    )


class ExportPlanBrandAndProductForm(forms.Form):
    story = forms.CharField(
        label='How we started',
        required=False,
        widget=Textarea(attrs={
            'placeholder': (
                'Dove Gin was founded in 2012 when Simon Dove started to distill gin in his garage in '
                'Shrewsbury. Simon came across a book of gin recipes on a visit to The Gin Museum of '
                'London. This inspired him to recreate gin distilled in the midlands 200 hundred years '
                'ago, with a modern twist.'
            ),
            'tooltip': (
                'Dove Gin was founded in 2012 when Simon Dove started to distill gin in his garage in '
                'Shrewsbury. Simon came across a book of gin recipes on a visit to The Gin Museum of London. '
                'This inspired him to recreate gin distilled in the midlands 200 hundred years ago, with a '
                'modern twist.'
            )}
        ),
    )
    location = forms.CharField(
        label="Where we're based",
        required=False,
        widget=Textarea(attrs={
            'placeholder': (
                'By 2015 the garage was too small for the volumes we produced so we moved to larger '
                'premises in rented, shared business space in Shrewsbury.'
            )}
        ),
    )
    processes = forms.CharField(
        label='How we make our products',
        required=False,
        widget=Textarea(attrs={
            'placeholder': (
                'We use vacuum distillation instead of traditional pot distillation. This  preserves '
                'the richness of flavour and aromas of the botanicals that give our gin its purity of '
                'taste.'
            )}
        ),
    )
    packaging = forms.CharField(
        label='Our packaging',
        required=False,
        widget=Textarea(attrs={
            'placeholder': (
                'From 2015 to 2018 sales have grown on average 31% a year. Revenue flattened off '
                'slightly in 2019 because of a UK distribution issue which has now been resolved. '
                'We are on track to meet our sales targets for 2020.'
            )}
        ),
    )


class ExportPlanBusinessObjectivesForm(forms.Form):
    rational = forms.CharField(
        label='Business performance',
        required=False,
        widget=Textarea(attrs={'placeholder': 'Add some text'})
    )
