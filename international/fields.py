import requests
from django import forms
from django.core.exceptions import ValidationError

from international_online_offer.core.region_sector_helpers import (
    generate_location_choices,
    get_full_sector_names_as_choices,
)
from international_online_offer.services import get_dbt_sectors


class DBTSectorsAPIMultipleChoiceField(forms.MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fetch_choices()

    def _fetch_choices(self):
        try:
            data = get_dbt_sectors()
            choices = get_full_sector_names_as_choices(data)
            self.choices = choices
        except requests.RequestException as e:
            raise ValidationError(f"Error fetching data from API: {e}")


class DBTRegionsMultipleChoiceField(forms.MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fetch_choices()

    def _fetch_choices(self):
        choices = generate_location_choices(include_cities=False)
        self.choices = choices
