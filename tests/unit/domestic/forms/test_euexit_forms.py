# TODO: use this when we port InternationalContactForm as part of contact/international/
# from directory_constants import choices

from core.constants import CONSENT_EMAIL
from domestic import forms


def test_domestic_contact_form_serialize(captcha_stub):
    form = forms.EUExitDomesticContactForm(
        # field_attributes as a param was supported in V1 but not in V2
        ingress_url='http://www.ingress.com',
        data={
            'first_name': 'test',
            'last_name': 'example',
            'email': 'test@example.com',
            'organisation_type': 'COMPANY',
            'company_name': 'thing',
            'comment': 'hello',
            'contact_consent': [CONSENT_EMAIL],
            'g-recaptcha-response': captcha_stub,
        },
    )
    assert form.is_valid()
    assert form.serialized_data == {
        'first_name': 'test',
        'last_name': 'example',
        'email': 'test@example.com',
        'organisation_type': 'COMPANY',
        'company_name': 'thing',
        'comment': 'hello',
        'ingress_url': 'http://www.ingress.com',
        'contact_consent': [CONSENT_EMAIL],
    }


# TODO: use this when we port euexit.forms.InternationalContactForm
# def test_international_contact_form_serialize(captcha_stub):
#     form = forms.InternationalContactForm(
#         # field_attributes as a param was supported in V1 but not in V2
#         ingress_url='http://www.ingress.com',
#         data={
#             'first_name': 'test',
#             'last_name': 'example',
#             'email': 'test@example.com',
#             'organisation_type': 'COMPANY',
#             'company_name': 'thing',
#             'country': choices.COUNTRY_CHOICES[1][0],
#             'city': 'London',
#             'comment': 'hello',
#             'terms_agreed': True,
#             'g-recaptcha-response': captcha_stub,
#         },
#     )

#     assert form.is_valid()
#     assert form.serialized_data == {
#         'first_name': 'test',
#         'last_name': 'example',
#         'email': 'test@example.com',
#         'organisation_type': 'COMPANY',
#         'company_name': 'thing',
#         'country': choices.COUNTRY_CHOICES[1][0],
#         'city': 'London',
#         'comment': 'hello',
#         'ingress_url': 'http://www.ingress.com',
#         'terms_agreed': True,
#     }
