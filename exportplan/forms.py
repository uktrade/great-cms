from great_components import forms
from django.forms import ImageField, Textarea

import directory_validators.url
import directory_validators.string
import directory_validators.file


class LogoForm(forms.Form):
    logo = ImageField(
        help_text=(
            'For best results this should be a transparent PNG file of 600 x '
            '600 pixels and no more than 2MB',
        ),
        required=True,
        validators=[directory_validators.file.logo_filesize, directory_validators.file.image_format]
    )


class ExportPlanBrandAndProductForm(forms.Form):
    story = forms.CharField(
        label='Story behind brand',
        required=False,
        widget=Textarea(attrs={
            'placeholder': (
                'Add some text, for example: We have since 1863 been distilling gin over five generations of our '
                'family using handed down process'
            )}
        ),
    )
    location = forms.CharField(
        label='Location',
        required=False,
        widget=Textarea(attrs={
            'placeholder': (
                'Add some text, for example: Distilled 1,200ft above sea level in ancient spring in the '
                'Peak District'
            )}
        ),
    )
    processes = forms.CharField(
        label='Manufacturing processes',
        required=False,
        widget=Textarea(attrs={
            'placeholder': (
                'Add some text, for example: The ingredients are ground by hand before being distilled '
                'in Cheshire. The alcohol vapour and the flavoursome oils from the botanicals reach our copper '
                'condenser, where they are immediately cooled'
            )}
        ),
    )
    packaging = forms.CharField(
        label='Packaging',
        required=False,
        widget=Textarea(attrs={
            'placeholder': (
                'Add some text, for example: hand made ceramic bottle hand sealed with wax'
            )}
        ),
    )
