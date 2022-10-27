import pytest
import requests
import requests_mock

from contact import constants, forms, views
from directory_api_client.exporting import url_lookup_by_postcode

routing_steps = [step for step, _ in views.RoutingFormView.form_list]

pytestmark = pytest.mark.django_db


@pytest.fixture
def domestic_data(captcha_stub):
    return {
        'given_name': 'Test',
        'family_name': 'Example',
        'email': 'test@example.com',
        'company_type': 'LIMITED',
        'organisation_name': 'Example corp',
        'postcode': 'ABC123',
        'comment': 'Help please',
        'g-recaptcha-response': captcha_stub,
        'terms_agreed': True,
    }


def test_short_notify_form_serialize_data(domestic_data):
    office_details = [
        {
            'is_match': True,
            'name': 'Some Office',
            'email': 'foo@example.com',
        },
    ]
    form = forms.ShortNotifyForm(data=domestic_data)

    assert form.is_valid()
    with requests_mock.mock() as mock:
        mock.get(
            url_lookup_by_postcode.format(postcode='ABC123'),
            json=office_details,
        )
        data = form.serialized_data

    assert data == {
        'given_name': 'Test',
        'family_name': 'Example',
        'email': 'test@example.com',
        'company_type': 'LIMITED',
        'company_type_other': '',
        'organisation_name': 'Example corp',
        'postcode': 'ABC123',
        'comment': 'Help please',
        'dit_regional_office_name': 'Some Office',
        'dit_regional_office_email': 'foo@example.com',
    }


def test_short_zendesk_form_serialize_data(domestic_data):
    office_details = {
        'name': 'Some Office',
        'email': 'foo@example.com',
    }
    form = forms.ShortZendeskForm(data=domestic_data)

    assert form.is_valid()
    with requests_mock.mock() as mock:
        mock.get(
            url_lookup_by_postcode.format(postcode='ABC123'),
            json=office_details,
        )
        data = form.serialized_data

    assert data == {
        'given_name': 'Test',
        'family_name': 'Example',
        'email': 'test@example.com',
        'company_type': 'LIMITED',
        'company_type_other': '',
        'organisation_name': 'Example corp',
        'postcode': 'ABC123',
        'comment': 'Help please',
    }
    assert form.full_name == 'Test Example'


@pytest.mark.parametrize(
    'form_data, is_valid',
    [
        (
            {
                'email': 'johndoe@mail.com',
                'last_name': 'john',
                'first_name': 'doe',
                'terms_agreed': True,
                'free_trade_agreements': ['FTA 1'],
                'company_already_exports': 'I_EXPORT_ALREADY',
            },
            True,
        ),
        (
            {
                'email': '',
                'last_name': '',
                'first_name': '',
                'terms_agreed': False,
                'free_trade_agreements': [],
                'company_already_exports': '',
            },
            False,
        ),
    ],
)
def test_fta_form_serialize_data(form_data, is_valid, mock_free_trade_agreements):
    form = forms.FTASubscribeForm(data=form_data)
    assert form.is_valid() == is_valid
    if is_valid:
        data = form.serialized_data
        assert form_data == data


def test_get_fta_choices(mock_free_trade_agreements):
    expected_choices = [
        ('FTA 1', 'FTA 1'),
        ('FTA 2', 'FTA 2'),
        ('FTA 3', 'FTA 3'),
        (constants.FUTURE_FTAS_CHOICE, constants.FUTURE_FTAS_CHOICE),
    ]
    choices = forms.FTASubscribeForm.get_fta_choices()
    assert choices == expected_choices


def test_domestic_contact_form_serialize_data_office_lookup_error(domestic_data):
    form = forms.ShortNotifyForm(data=domestic_data)

    assert form.is_valid()

    with requests_mock.mock() as mock:
        mock.get(
            url_lookup_by_postcode.format(postcode='ABC123'),
            exc=requests.exceptions.ConnectTimeout,
        )
        data = form.serialized_data

    assert data['dit_regional_office_name'] == ''
    assert data['dit_regional_office_email'] == ''


def test_domestic_contact_form_serialize_data_office_lookup_not_found(domestic_data):
    form = forms.ShortNotifyForm(data=domestic_data)

    assert form.is_valid()

    with requests_mock.mock() as mock:
        mock.get(url_lookup_by_postcode.format(postcode='ABC123'), status_code=404)
        data = form.serialized_data

    assert data['dit_regional_office_name'] == ''
    assert data['dit_regional_office_email'] == ''


def test_domestic_contact_form_serialize_data_office_lookup_none_returned(domestic_data):
    form = forms.ShortNotifyForm(data=domestic_data)

    assert form.is_valid()

    with requests_mock.mock() as mock:
        mock.get(url_lookup_by_postcode.format(postcode='ABC123'), json=None)

    data = form.serialized_data

    assert data['dit_regional_office_name'] == ''
    assert data['dit_regional_office_email'] == ''


def test_feedback_form_serialize_data(captcha_stub):
    form = forms.FeedbackForm(
        data={
            'name': 'Test Example',
            'email': 'test@example.com',
            'comment': 'Help please',
            'g-recaptcha-response': captcha_stub,
            'terms_agreed': True,
        }
    )

    assert form.is_valid()
    assert form.serialized_data == {
        'name': 'Test Example',
        'email': 'test@example.com',
        'comment': 'Help please',
    }
    assert form.full_name == 'Test Example'


def test_marketing_form_validations(valid_request_export_support_form_data):
    form = forms.ExportSupportForm(data=valid_request_export_support_form_data)
    assert form.is_valid()
    assert form.cleaned_data['first_name'] == valid_request_export_support_form_data['first_name']
    assert form.cleaned_data['email'] == valid_request_export_support_form_data['email']

    # validate the form with blank 'annual_turnover' field
    valid_request_export_support_form_data['annual_turnover'] = ''
    form = forms.ExportSupportForm(data=valid_request_export_support_form_data)
    assert form.is_valid()
    assert form.cleaned_data['first_name'] == valid_request_export_support_form_data['first_name']
    assert form.cleaned_data['email'] == valid_request_export_support_form_data['email']
    assert form.cleaned_data['annual_turnover'] == ''


def test_marketing_form_api_serialization(valid_request_export_support_form_data):
    form = forms.ExportSupportForm(data=valid_request_export_support_form_data)
    assert form.is_valid()
    api_data = form.serialized_data
    employees_number_label = dict(forms.ExportSupportForm.EMPLOYEES_NUMBER_CHOICES).get(
        form.serialized_data['employees_number']
    )
    assert api_data['employees_number_label'] == employees_number_label


@pytest.mark.parametrize(
    'invalid_data,invalid_field,error_message',
    (
        (
            {
                'email': 'test@test.com',
                'phone_number': '+447500192913',
                'company_name': 'Limited',
                'company_location': 'London',
                'sector': '3',
                'company_website': 'limitedgoal.com',
                'employees_number': '1',
                'currently_export': 'no',
                'advertising_feedback': '4',
            },
            'first_name',
            'Enter your first name',
        ),
        (
            {
                'first_name': 'Test',
                'phone_number': '+447500192913',
                'company_name': 'Limited',
                'company_location': 'London',
                'sector': '3',
                'company_website': 'limitedgoal.com',
                'employees_number': '1',
                'currently_export': 'no',
                'advertising_feedback': '4',
            },
            'email',
            'Enter an email address in the correct format,' ' like name@example.com',
        ),
        (
            {
                'first_name': 'Test name',
                'email': 'test@test.com',
                'phone_number': '++00192913',  # invalid field data
                'company_name': 'Limited',
                'company_location': 'London',
                'sector': '3',
                'company_website': 'limitedgoal.com',
                'employees_number': '1',
                'currently_export': 'no',
                'advertising_feedback': '4',
            },
            'phone_number',
            'Please enter a UK phone number',
        ),
        (
            {
                'first_name': 'Test name',
                'email': 'test@test.com',
                'company_name': 'Limited',
                'company_location': 'London',
                'sector': '3',
                'company_website': 'limitedgoal.com',
                'employees_number': '1',
                'currently_export': 'no',
                'advertising_feedback': '4',
            },
            'phone_number',
            'Enter a UK phone number',
        ),
    ),
)
def test_marketing_form_validation_errors(invalid_data, invalid_field, error_message):
    form = forms.ExportSupportForm(data=invalid_data)
    assert not form.is_valid()
    assert invalid_field in form.errors
    assert form.errors[invalid_field][0] == error_message


def test_phone_number_validation(valid_request_export_support_form_data):
    form = forms.ExportSupportForm(data=valid_request_export_support_form_data)
    assert form.is_valid()

    # validate a phone number without country code
    valid_request_export_support_form_data['phone_number'] = '07501234567'
    form = forms.ExportSupportForm(data=valid_request_export_support_form_data)
    assert form.is_valid()

    # # validate a phone number with spaces
    valid_request_export_support_form_data['phone_number'] = '+44 0750 123 45 67'
    form = forms.ExportSupportForm(data=valid_request_export_support_form_data)
    assert form.is_valid()

    # # validate a phone number with country code
    valid_request_export_support_form_data['phone_number'] = '+447501234567'
    form = forms.ExportSupportForm(data=valid_request_export_support_form_data)
    assert form.is_valid()


def test_postcode_validation(valid_request_export_support_form_data):
    form = forms.ExportSupportForm(data=valid_request_export_support_form_data)
    assert form.is_valid()

    # validate a phone number without spaces
    valid_request_export_support_form_data['company_postcode'] = 'W1A1AA'
    form = forms.ExportSupportForm(data=valid_request_export_support_form_data)
    assert form.is_valid()

    # # validate a postcode with spaces
    valid_request_export_support_form_data['company_postcode'] = 'W1A 1AA'
    form = forms.ExportSupportForm(data=valid_request_export_support_form_data)
    assert form.is_valid()

    # # validate a postcode with mixed case
    valid_request_export_support_form_data['company_postcode'] = 'w1a 1Aa'
    form = forms.ExportSupportForm(data=valid_request_export_support_form_data)
    assert form.is_valid()

    # # check invalid postcode format fails
    valid_request_export_support_form_data['company_postcode'] = 'W1A W1A'
    form = forms.ExportSupportForm(data=valid_request_export_support_form_data)
    assert form.is_valid() is False


def test_location_form_routing():
    field = forms.LocationRoutingForm.base_fields['choice']
    # for each of the choices the form supports
    for choice, _ in field.choices:
        # the view supports routing the user to that triage step
        assert choice in ['domestic', 'international']


def test_domestic_form_routing():
    field = forms.DomesticRoutingForm.base_fields['choice']
    choices = set(item for item, _ in field.choices)

    # expect these choices to result in a redirect to a new form
    choices_expect_redirect = {
        constants.TRADE_OFFICE,
        constants.EXPORT_ADVICE,
        constants.FINANCE,
        constants.EVENTS,
        constants.DSO,
        constants.OTHER,
    }
    mapping = views.RoutingFormView.redirect_mapping[constants.DOMESTIC]

    for choice in choices_expect_redirect:
        assert choice in choices
        assert choice in mapping
        assert choice not in routing_steps

    choices_expect_next_step = (constants.GREAT_SERVICES,)
    for choice in choices_expect_next_step:
        assert choice in choices
        assert choice not in mapping
        assert choice in routing_steps

    expected_choice_count = len(choices_expect_next_step) + len(choices_expect_redirect)

    assert expected_choice_count == len(choices)


def test_great_services_form_routing():
    field = forms.GreatServicesRoutingForm.base_fields['choice']
    choices = set(item for item, _ in field.choices)

    choices_expect_redirect = {
        constants.OTHER,
    }
    mapping = views.RoutingFormView.redirect_mapping[constants.GREAT_SERVICES]

    for choice in choices_expect_redirect:
        assert choice in choices
        assert choice in mapping
        assert choice not in routing_steps

    choices_expect_next_step = {
        constants.EXPORT_OPPORTUNITIES,
        constants.GREAT_ACCOUNT,
    }
    for choice in choices_expect_next_step:
        assert choice in choices
        assert choice not in mapping
        assert choice in routing_steps

    expected_choice_count = len(choices_expect_next_step) + len(choices_expect_redirect)

    assert expected_choice_count == len(choices)


def test_export_opportunities_form_routing():
    field = forms.ExportOpportunitiesRoutingForm.base_fields['choice']

    mapping = views.RoutingFormView.redirect_mapping[constants.EXPORT_OPPORTUNITIES]

    for choice, _ in field.choices:
        assert choice in mapping
        assert choice not in routing_steps


def test_form_choices__great_account_routing_form():

    expected = (
        (constants.NO_VERIFICATION_EMAIL, 'I have not received my email confirmation'),
        (constants.PASSWORD_RESET, 'I need to reset my password'),
        (constants.COMPANY_NOT_FOUND, 'I cannot find my company'),
        (constants.COMPANIES_HOUSE_LOGIN, 'My Companies House login is not working'),
        (constants.VERIFICATION_CODE, 'I do not know where to enter my verification code'),
        (constants.NO_VERIFICATION_LETTER, 'I have not received my letter containing the verification code'),
        (constants.NO_VERIFICATION_MISSING, 'I have not received a verification code'),
        (constants.OTHER, 'Other'),
    )

    choices = tuple(forms.GreatAccountRoutingForm().fields['choice'].choices)
    assert choices == forms.great_account_choices()
    assert choices == expected


def test_feedback_form_full_name(captcha_stub):

    form_instance = forms.FeedbackForm(
        data={
            'name': 'Alice McTest',
            'email': 'Alice.McTest@example.com',
            'comment': 'I am Alice McTest and I am using your website',
            'g-recaptcha-response': captcha_stub,
            'terms_agreed': True,
        }
    )

    assert form_instance.full_name == 'Alice McTest'


def test_selling_online_overseas_applicant_valid_form_ch():
    form = forms.SellingOnlineOverseasApplicant(
        data={
            'company_name': 'Acme',
            'company_number': '123',
            'company_address': 'Same Street',
            'website_address': 'bar',
            'turnover': 'Under 100k',
        }
    )
    assert form.is_valid()


def test_selling_online_overseas_applicant_valid_form_non_ch():
    form = forms.SellingOnlineOverseasApplicantNonCH(
        data={
            'company_name': 'Acme',
            'company_address': 'Same Street',
            'website_address': 'bar',
            'turnover': 'Under 100k',
        }
    )
    assert form.is_valid()


def test_selling_online_overseas_applicant_valid_form_individual():
    form = forms.SellingOnlineOverseasApplicantIndividual(
        data={
            'company_name': 'Acme',
            'company_number': '123',
            'company_address': 'Same Street',
            'company_postcode': 'SW1H 0TL',
            'website_address': 'bar',
            'turnover': 'Under 100k',
        }
    )
    assert form.is_valid()


def test_selling_online_overseas_contact_details_form__editable_fields():

    form_1 = forms.SellingOnlineOverseasContactDetails(
        initial={
            'contact_first_name': 'Alice',
            'contact_last_name': 'McTest',
            'contact_email': 'alice@example.com',
            'phone': '998877665544',
        }
    )
    assert form_1.fields['contact_first_name'].disabled is True
    assert form_1.fields['contact_first_name'].required is False
    assert form_1.fields['contact_first_name'].container_css_classes == 'border-active-blue read-only-input-container '

    assert form_1.fields['contact_last_name'].disabled is True
    assert form_1.fields['contact_last_name'].required is False
    assert form_1.fields['contact_last_name'].container_css_classes == 'border-active-blue read-only-input-container '

    assert form_1.fields['contact_email'].disabled is True
    assert form_1.fields['contact_email'].required is False
    assert form_1.fields['contact_email'].container_css_classes == (
        'border-active-blue read-only-input-container padding-bottom-0 margin-bottom-30 '
    )

    assert form_1.fields['phone'].disabled is False
    assert form_1.fields['phone'].required is True
    assert form_1.fields['phone'].container_css_classes == 'form-group '

    form_2 = forms.SellingOnlineOverseasContactDetails(
        initial={
            'contact_first_name': 'Alice',
            'contact_email': 'alice@example.com',
            'phone': '998877665544',
        }
    )
    assert form_2.fields['contact_first_name'].disabled is True
    assert form_2.fields['contact_first_name'].required is False
    assert form_2.fields['contact_first_name'].container_css_classes == 'border-active-blue read-only-input-container '

    assert form_2.fields['contact_last_name'].disabled is False
    assert form_2.fields['contact_last_name'].required is True
    assert form_2.fields['contact_last_name'].container_css_classes == 'form-group '

    assert form_2.fields['contact_email'].disabled is True
    assert form_2.fields['contact_email'].required is False
    assert form_2.fields['contact_email'].container_css_classes == (
        'border-active-blue read-only-input-container padding-bottom-0 margin-bottom-30 '
    )

    assert form_2.fields['phone'].disabled is False
    assert form_2.fields['phone'].required is True
    assert form_2.fields['phone'].container_css_classes == 'form-group '

    form_3 = forms.SellingOnlineOverseasContactDetails(
        initial={
            'contact_last_name': 'McTest',
            'contact_email': 'alice@example.com',
            'phone': '998877665544',
        }
    )
    assert form_3.fields['contact_first_name'].disabled is False
    assert form_3.fields['contact_first_name'].required is True
    assert form_3.fields['contact_first_name'].container_css_classes == 'form-group '

    assert form_3.fields['contact_last_name'].disabled is True
    assert form_3.fields['contact_last_name'].required is False
    assert form_3.fields['contact_last_name'].container_css_classes == 'border-active-blue read-only-input-container '

    assert form_3.fields['contact_email'].disabled is True
    assert form_3.fields['contact_email'].required is False
    assert form_3.fields['contact_email'].container_css_classes == (
        'border-active-blue read-only-input-container padding-bottom-0 margin-bottom-30 '
    )

    assert form_3.fields['phone'].disabled is False
    assert form_3.fields['phone'].required is True
    assert form_3.fields['phone'].container_css_classes == 'form-group '

    form_4 = forms.SellingOnlineOverseasContactDetails(
        initial={
            'contact_email': 'alice@example.com',
            'phone': '998877665544',
        }
    )
    assert form_4.fields['contact_first_name'].disabled is False
    assert form_4.fields['contact_first_name'].required is True
    assert form_4.fields['contact_first_name'].container_css_classes == 'form-group '

    assert form_4.fields['contact_last_name'].disabled is False
    assert form_4.fields['contact_last_name'].required is True
    assert form_4.fields['contact_last_name'].container_css_classes == 'form-group '

    assert form_4.fields['contact_email'].disabled is True
    assert form_4.fields['contact_email'].required is False
    assert form_4.fields['contact_email'].container_css_classes == (
        'border-active-blue read-only-input-container padding-bottom-0 margin-bottom-30 '
    )

    assert form_4.fields['phone'].disabled is False
    assert form_4.fields['phone'].required is True
    assert form_4.fields['phone'].container_css_classes == 'form-group '

    form_5 = forms.SellingOnlineOverseasContactDetails(initial={})
    assert form_5.fields['contact_first_name'].disabled is False
    assert form_5.fields['contact_first_name'].required is True
    assert form_5.fields['contact_first_name'].container_css_classes == 'form-group '

    assert form_5.fields['contact_last_name'].disabled is False
    assert form_5.fields['contact_last_name'].required is True
    assert form_5.fields['contact_last_name'].container_css_classes == 'form-group '

    assert form_5.fields['contact_email'].disabled is True
    assert form_5.fields['contact_email'].required is False
    assert form_5.fields['contact_email'].container_css_classes == (
        'border-active-blue read-only-input-container padding-bottom-0 margin-bottom-30 '
    )

    assert form_5.fields['phone'].disabled is False
    assert form_5.fields['phone'].required is True
    assert form_5.fields['phone'].container_css_classes == 'form-group '
