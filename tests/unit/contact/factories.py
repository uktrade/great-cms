import factory.fuzzy
from factory.django import DjangoModelFactory

from contact.models import DPEFormToZendeskFieldMapping


class DPEFormToZendeskFieldMappingFactory(DjangoModelFactory):
    class Meta:
        model = DPEFormToZendeskFieldMapping

    dpe_form_field_id = factory.fuzzy.FuzzyText(length=15)
    zendesk_field_id = factory.fuzzy.FuzzyText(length=15)
    dpe_form_value_to_zendesk_field_value = None
