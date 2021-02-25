import http
from io import BytesIO
from profile.business_profile import constants, forms, helpers, views
from unittest import mock

import pytest
from directory_api_client.client import api_client
from directory_constants import urls, user_roles
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.forms import NON_FIELD_ERRORS
from django.urls import reverse
from formtools.wizard.views import normalize_name
from PIL import Image, ImageDraw
from requests.exceptions import HTTPError

from core.tests.helpers import create_response, submit_step_factory


def create_test_image(extension):
    image = Image.new('RGB', (300, 50))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), 'This text is drawn on image')
    byte_io = BytesIO()
    image.save(byte_io, extension)
    byte_io.seek(0)
    return byte_io


@pytest.fixture
def company_profile_data():
    return {
        'name': 'Cool Company',
        'is_publishable': True,
        'expertise_products_services': {},
        'is_identity_check_message_sent': False,
        'is_published_find_a_supplier': False,
        'number': '1234567',
        'slug': 'cool-company',
        'created': '2012-06-15T13:45:30.00000Z',
        'modified': '2019-04-05T06:43:23.00000Z',
    }


@pytest.fixture
def default_private_case_study(case_study_data):
    return {
        **case_study_data[views.BASIC],
        **case_study_data[views.MEDIA],
        'image_one': 'https://example.com/image-one.png',
        'image_two': 'https://example.com/image-two.png',
        'image_three': 'https://example.com/image-three.png',
    }


@pytest.fixture(autouse=True)
def mock_case_study_retrieve(default_private_case_study):
    patch = mock.patch.object(
        api_client.company, 'case_study_retrieve', return_value=create_response(default_private_case_study)
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_case_study_update():
    patch = mock.patch.object(api_client.company, 'case_study_update', return_value=create_response())
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_case_study_create():
    patch = mock.patch.object(api_client.company, 'case_study_create', return_value=create_response(201))
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_retrieve_company(company_profile_data):
    response = create_response(company_profile_data)
    patch = mock.patch.object(api_client.company, 'profile_retrieve', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_update_company():
    patch = mock.patch.object(api_client.company, 'profile_update', return_value=create_response())
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_retrieve_supplier():
    patch = mock.patch.object(
        api_client.supplier,
        'retrieve_profile',
        return_value=create_response({'is_company_owner': True, 'role': user_roles.ADMIN}),
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_collaborator_role_update():
    patch = mock.patch.object(api_client.company, 'collaborator_role_update', return_value=create_response())
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_collaborator_list(user):
    response = create_response(
        [
            {'sso_id': user.id, 'role': user_roles.ADMIN, 'company_email': user.email, 'name': 'jim example'},
            {'sso_id': 1234, 'role': user_roles.EDITOR, 'company_email': 'jim@example.com', 'name': 'bob example'},
        ]
    )
    patch = mock.patch.object(api_client.company, 'collaborator_list', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_collaboration_request_list(user):
    response = create_response(
        [
            {'requestor_sso_id': user.id, 'uuid': 1234, 'name': 'jim example', 'accepted': False},
            {'requestor_sso_id': 1234, 'uuid': 1234, 'name': 'bob example', 'accepted': False},
        ]
    )
    patch = mock.patch.object(api_client.company, 'collaboration_request_list', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_collaborator_invite_list(user):
    response = create_response(
        [
            {
                'uuid': '7b4f5c1d-a299-4cb7-aa8e-261101c643de',
                'collaborator_email': 'jim@example.com',
                'company': 1,
                'requestor': 2,
                'requestor_email': 'requestor@testme.com',
                'requestor_sso_id': 3,
                'accepted': False,
                'role': user_roles.EDITOR,
            }
        ]
    )
    patch = mock.patch.object(api_client.company, 'collaborator_invite_list', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture
def submit_case_study_create_step(client):
    return submit_step_factory(
        client=client, url_name='business-profile-case-study', view_class=views.CaseStudyWizardCreateView
    )


@pytest.fixture
def submit_case_study_edit_step(client):
    url_name = 'business-profile-case-study-edit'
    view_class = views.CaseStudyWizardEditView
    view_name = normalize_name(view_class.__name__)
    step_names = iter([name for name, form in view_class.form_list])

    def submit_step(data, step_name=None):
        step_name = step_name or next(step_names)
        url = reverse(url_name, kwargs={'step': step_name, 'id': 1})
        response = client.get(url)
        assert response.status_code == 200
        return client.post(
            url,
            {view_name + '-current_step': step_name, **{step_name + '-' + key: value for key, value in data.items()}},
        )

    return submit_step


@pytest.fixture
def case_study_data():
    return {
        views.BASIC: {
            'title': 'Example',
            'description': 'Great',
            'short_summary': 'Nice',
            'sector': 'AEROSPACE',
            'website': 'http://www.example.com',
            'keywords': 'good, great',
        },
        views.MEDIA: {
            'testimonial': 'Great',
            'testimonial_name': 'Neville',
            'testimonial_job_title': 'Abstract hat maker',
            'testimonial_company': 'Imaginary hats Ltd',
            'image_one': SimpleUploadedFile(
                name='image-one.png', content=create_test_image('png').read(), content_type='image/png'
            ),
            'image_two': SimpleUploadedFile(
                name='image-two.png', content=create_test_image('png').read(), content_type='image/png'
            ),
            'image_three': '',
            'image_one_caption': 'nice image',
            'image_two_caption': 'thing',
            'image_three_caption': 'thing',
        },
    }


def test_find_a_buyer_unauthenticated_enrolment(client):
    profile_url = reverse('business-profile')
    enrolment_url = reverse('enrolment-start')
    response = client.get(profile_url)

    assert response.status_code == http.client.FOUND
    assert response.url == f'{enrolment_url}?next={profile_url}'


def test_supplier_company_retrieve_found_business_profile_on(mock_retrieve_company, client, company_profile_data, user):
    client.force_login(user)
    mock_retrieve_company.return_value = create_response(company_profile_data)

    response = client.get(reverse('business-profile'))

    assert response.template_name == ['business_profile/profile.html']


@pytest.mark.parametrize('param', ('owner-transferred', 'user-added', 'user-removed'))
def test_success_message(mock_retrieve_supplier, client, param, user):
    client.force_login(user)
    mock_retrieve_supplier.return_value = create_response({'role': user_roles.EDITOR})

    url = reverse('business-profile')
    response = client.get(url, {param: True})
    for message in response.context['messages']:
        assert str(message) == views.BusinessProfileView.SUCCESS_MESSAGES[param]


edit_urls = (
    reverse('business-profile-description'),
    reverse('business-profile-email'),
    reverse('business-profile-social'),
    reverse('business-profile-website'),
    reverse('business-profile-expertise-regional'),
    reverse('business-profile-expertise-countries'),
    reverse('business-profile-expertise-industries'),
    reverse('business-profile-expertise-languages'),
)

edit_data = (
    {'description': 'A description', 'summary': 'A summary'},
    {'email_address': 'email@example.com'},
    {
        'facebook_url': 'https://www.facebook.com/thing/',
        'twitter_url': 'https://www.twitter.com/thing/',
        'linkedin_url': 'https://www.linkedin.com/thing/',
    },
    {'website': 'https://www.mycompany.com/'},
    {'expertise_regions': ['WEST_MIDLANDS']},
    {'expertise_countries': ['AL']},
    {'expertise_industries': ['POWER']},
    {'expertise_languages': ['ab']},
)


@pytest.mark.parametrize('url', edit_urls)
def test_edit_page_initial_data(client, url, company_profile_data, user):
    client.force_login(user)
    company = helpers.CompanyParser(company_profile_data)

    response = client.get(url)
    assert response.context_data['form'].initial == (company.serialize_for_form())


success_urls = (
    reverse('business-profile'),
    reverse('business-profile'),
    reverse('business-profile'),
    reverse('business-profile'),
    reverse('business-profile-expertise-routing'),
    reverse('business-profile-expertise-routing'),
    reverse('business-profile-expertise-routing'),
    reverse('business-profile-expertise-routing'),
)


@pytest.mark.parametrize('url,data,success_url', zip(edit_urls, edit_data, success_urls))
def test_edit_page_submmit_success(client, mock_update_company, user, url, data, success_url):
    client.force_login(user)
    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == success_url
    assert mock_update_company.call_count == 1
    assert mock_update_company.call_args == mock.call(sso_session_id=user.session_id, data=data)


def test_publish_not_publishable(client, user, mock_retrieve_company, company_profile_data):
    client.force_login(user)
    mock_retrieve_company.return_value = create_response({**company_profile_data, 'is_publishable': False})

    url = reverse('business-profile-publish')

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('business-profile')


def test_publish_publishable(client, user, mock_retrieve_company):
    client.force_login(user)
    url = reverse('business-profile-publish')

    response = client.get(url)

    assert response.status_code == 200


def test_edit_page_submmit_publish_success(client, mock_update_company, user):
    client.force_login(user)
    url = reverse('business-profile-publish')
    data = {'is_published_investment_support_directory': True, 'is_published_find_a_supplier': True}
    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == reverse('business-profile')
    assert mock_update_company.call_count == 1
    assert mock_update_company.call_args == mock.call(sso_session_id=user.session_id, data=data)


def test_edit_page_submmit_publish_context(client, company_profile_data, user):
    client.force_login(user)
    company = helpers.CompanyParser(company_profile_data)

    url = reverse('business-profile-publish')
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['company'] == company.serialize_for_template()


def test_edit_page_logo_submmit_success(client, mock_update_company, user):
    client.force_login(user)
    url = reverse('business-profile-logo')
    data = {
        'logo': SimpleUploadedFile(name='image.png', content=create_test_image('png').read(), content_type='image/png')
    }

    response = client.post(url, data)

    assert response.status_code == 302
    assert response.url == reverse('business-profile')
    assert mock_update_company.call_count == 1
    assert mock_update_company.call_args == mock.call(sso_session_id=user.session_id, data={'logo': mock.ANY})


@pytest.mark.parametrize('url,data', zip(edit_urls, edit_data))
def test_edit_page_submmit_error(client, mock_update_company, url, data, user):
    client.force_login(user)
    mock_update_company.return_value = create_response(status_code=400)

    with pytest.raises(HTTPError):
        client.post(url, data)


def test_case_study_create(submit_case_study_create_step, mock_case_study_create, case_study_data, client, user):
    client.force_login(user)

    response = submit_case_study_create_step(case_study_data[views.BASIC])
    assert response.status_code == 302

    response = submit_case_study_create_step(case_study_data[views.MEDIA])
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.url == reverse('business-profile')

    assert mock_case_study_create.call_count == 1


def test_case_study_edit_foo(
    submit_case_study_edit_step,
    mock_case_study_retrieve,
    client,
    mock_case_study_update,
    case_study_data,
    default_private_case_study,
    user,
    rf,
):
    client.force_login(user)

    response = submit_case_study_edit_step(case_study_data[views.BASIC])
    assert response.status_code == 302

    response = submit_case_study_edit_step(case_study_data[views.MEDIA])
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.url == reverse('business-profile')
    assert mock_case_study_update.call_count == 1
    data = {**default_private_case_study, 'image_one': mock.ANY, 'image_two': mock.ANY}
    del data['image_three']

    assert mock_case_study_update.call_args == mock.call(case_study_id='1', data=data, sso_session_id='123')


def test_case_study_edit_not_found(mock_case_study_retrieve, client, user):
    mock_case_study_retrieve.return_value = create_response(status_code=404)

    client.force_login(user)
    url = reverse('business-profile-case-study-edit', kwargs={'id': '1', 'step': views.BASIC})

    response = client.get(url)

    assert response.status_code == 404


def test_case_study_edit_found(mock_case_study_retrieve, client, user):
    client.force_login(user)
    url = reverse('business-profile-case-study-edit', kwargs={'id': '1', 'step': views.BASIC})

    response = client.get(url)

    assert response.status_code == 200


def test_business_details_sole_trader(settings, mock_retrieve_company, client, user):
    client.force_login(user)
    mock_retrieve_company.return_value = create_response({'company_type': 'SOLE_TRADER'})

    url = reverse('business-profile-business-details')

    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.context_data['form'], forms.NonCompaniesHouseBusinessDetailsForm)


def test_business_details_companies_house(settings, client, mock_retrieve_company, user):
    client.force_login(user)
    mock_retrieve_company.return_value = create_response({'company_type': 'COMPANIES_HOUSE'})

    url = reverse('business-profile-business-details')

    response = client.get(url)

    assert response.status_code == 200
    assert isinstance(response.context_data['form'], forms.CompaniesHouseBusinessDetailsForm)


@pytest.mark.parametrize(
    'choice,expected_url',
    (
        (forms.ExpertiseRoutingForm.REGION, reverse('business-profile-expertise-regional')),
        (forms.ExpertiseRoutingForm.COUNTRY, reverse('business-profile-expertise-countries')),
        (forms.ExpertiseRoutingForm.INDUSTRY, reverse('business-profile-expertise-industries')),
        (forms.ExpertiseRoutingForm.LANGUAGE, reverse('business-profile-expertise-languages')),
    ),
)
def test_add_expertise_routing(settings, choice, expected_url, client, user):
    client.force_login(user)

    url = reverse('business-profile-expertise-routing')

    response = client.post(url, {'choice': choice})

    assert response.status_code == 302
    assert response.url == expected_url


def test_expertise_routing_form(client, settings, user):
    client.force_login(user)
    url = reverse('business-profile-expertise-routing')

    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['company']


def test_expertise_products_services_routing_form_context(client, settings, company_profile_data, user):
    client.force_login(user)

    company = helpers.CompanyParser(company_profile_data)

    url = reverse('business-profile-expertise-products-services-routing')

    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['company'] == company.serialize_for_template()


@pytest.mark.parametrize('choice', (item for item, _ in forms.ExpertiseProductsServicesRoutingForm.CHOICES if item))
def test_expertise_products_services_routing_form(choice, client, settings, user):
    client.force_login(user)

    url = reverse('business-profile-expertise-products-services-routing')

    response = client.post(url, {'choice': choice})

    assert response.url == reverse('business-profile-expertise-products-services', kwargs={'category': choice})


def test_products_services_form_prepopulate(mock_retrieve_company, company_profile_data, client, user):
    client.force_login(user)
    mock_retrieve_company.return_value = create_response(
        {
            **company_profile_data,
            'expertise_products_services': {
                constants.LEGAL: ['Company incorporation', 'Employment'],
                constants.PUBLICITY: ['Public Relations', 'Branding'],
            },
        }
    )

    url = reverse('business-profile-expertise-products-services', kwargs={'category': constants.PUBLICITY})
    response = client.get(url)

    assert response.context_data['form'].initial == {'expertise_products_services': 'Public Relations|Branding'}


def test_products_services_other_form(mock_retrieve_company, company_profile_data, client, user):
    client.force_login(user)
    mock_retrieve_company.return_value = create_response(
        {
            **company_profile_data,
            'expertise_products_services': {
                constants.LEGAL: ['Company incorporation', 'Employment'],
                constants.OTHER: ['Foo', 'Bar'],
            },
        }
    )

    url = reverse('business-profile-expertise-products-services-other')
    response = client.get(url)

    assert response.context_data['form'].initial == {'expertise_products_services': 'Foo, Bar'}


def test_products_services_other_form_update(
    client, mock_retrieve_company, mock_update_company, user, company_profile_data
):
    client.force_login(user)
    mock_retrieve_company.return_value = create_response(
        {
            **company_profile_data,
            'expertise_products_services': {
                constants.LEGAL: ['Company incorporation', 'Employment'],
                constants.OTHER: ['Foo', 'Bar'],
            },
        }
    )

    url = reverse('business-profile-expertise-products-services-other')

    client.post(url, {'expertise_products_services': 'Baz,Zad'})

    assert mock_update_company.call_count == 1
    assert mock_update_company.call_args == mock.call(
        data={
            'expertise_products_services': {
                constants.LEGAL: ['Company incorporation', 'Employment'],
                constants.OTHER: ['Baz', 'Zad'],
            }
        },
        sso_session_id='123',
    )


def test_products_services_form_update(client, mock_retrieve_company, mock_update_company, user, company_profile_data):
    client.force_login(user)
    mock_retrieve_company.return_value = create_response(
        {
            **company_profile_data,
            'expertise_products_services': {
                constants.LEGAL: ['Company incorporation', 'Employment'],
                constants.PUBLICITY: ['Public Relations', 'Branding'],
            },
        }
    )

    url = reverse('business-profile-expertise-products-services', kwargs={'category': constants.PUBLICITY})
    client.post(url, {'expertise_products_services': ['Social Media']})

    assert mock_update_company.call_count == 1
    assert mock_update_company.call_args == mock.call(
        data={
            'expertise_products_services': {
                constants.LEGAL: ['Company incorporation', 'Employment'],
                constants.PUBLICITY: ['Social Media'],
            }
        },
        sso_session_id='123',
    )


def test_products_services_exposes_category(client, user):
    client.force_login(user)

    url = reverse('business-profile-expertise-products-services', kwargs={'category': constants.BUSINESS_SUPPORT})
    response = client.get(url)

    assert response.context_data['category'] == 'business support'


def test_personal_details(client, mock_create_user_profile, user):
    client.force_login(user)

    data = {
        'given_name': 'Foo',
        'family_name': 'Example',
        'job_title': 'Exampler',
        'phone_number': '1232342',
        'confirmed_is_company_representative': True,
        'terms_agreed': True,
    }
    response = client.post(reverse('business-profile-personal-details'), data)

    assert response.status_code == 302
    assert response.url == reverse('business-profile')
    assert mock_create_user_profile.call_count == 1
    assert mock_create_user_profile.call_args == mock.call(
        sso_session_id=user.session_id,
        data={'first_name': 'Foo', 'last_name': 'Example', 'job_title': 'Exampler', 'mobile_phone_number': '1232342'},
    )


@mock.patch.object(api_client.company, 'verify_identity_request')
def test_request_identity_verification(mock_verify_identity_request, client, user, settings):
    mock_verify_identity_request.return_value = create_response()

    client.force_login(user)

    url = reverse('business-profile-request-to-verify')

    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('business-profile')
    assert mock_verify_identity_request.call_count == 1
    assert mock_verify_identity_request.call_args == mock.call(user.session_id)

    response = client.get(response.url)
    assert response.status_code == 200
    for message in response.context['messages']:
        assert str(message) == views.IdentityVerificationRequestFormView.success_message


@mock.patch.object(api_client.company, 'verify_identity_request')
def test_request_identity_verification_already_sent(mock_verify_identity_request, client, user):
    user.company.data['is_identity_check_message_sent'] = True
    client.force_login(user)

    url = reverse('business-profile-request-to-verify')

    response = client.post(url)
    assert response.status_code == 302
    assert response.url == reverse('business-profile')
    assert mock_verify_identity_request.call_count == 0


def test_collaborator_list(mock_collaborator_list, mock_collaboration_request_list, client, user, settings):
    client.force_login(user)
    mock_collaborator_list.return_value = create_response([])
    mock_collaboration_request_list.return_value = create_response([])

    url = reverse('business-profile-admin-tools')
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['collaborators'] == []
    assert response.context_data['collaboration_requests'] == []


@pytest.mark.parametrize('role', (user_roles.EDITOR, user_roles.MEMBER))
def test_edit_collaborator_not_admin(mock_retrieve_supplier, mock_collaborator_list, client, user, role):
    mock_retrieve_supplier.return_value = create_response({'is_company_owner': False, 'role': role})
    client.force_login(user)

    url = reverse('business-profile-admin-collaborator-edit', kwargs={'sso_id': 1234})
    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith(reverse('business-profile'))
    assert mock_collaborator_list.call_count == 0


def test_edit_collaborator_edit_not_found(client, user):
    client.force_login(user)

    url = reverse('business-profile-admin-collaborator-edit', kwargs={'sso_id': 43})
    response = client.get(url)

    assert response.status_code == 404


def test_edit_collaborator_edit_self(client, user):
    client.force_login(user)

    url = reverse('business-profile-admin-collaborator-edit', kwargs={'sso_id': user.id})
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('business-profile-admin-tools')


def test_edit_collaborator_retrieve(client, user):
    client.force_login(user)

    url = reverse('business-profile-admin-collaborator-edit', kwargs={'sso_id': 1234})
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.parametrize('action', (forms.CHANGE_COLLABORATOR_TO_MEMBER, forms.CHANGE_COLLABORATOR_TO_ADMIN))
def test_edit_collaborator_change_editor_to_other(mock_collaborator_list, client, user, action):
    mock_collaborator_list.return_value = create_response(
        [
            {'sso_id': user.id, 'role': user_roles.ADMIN, 'company_email': user.email},
            {'sso_id': 1234, 'role': user_roles.EDITOR, 'company_email': 'jim@example.com'},
        ]
    )
    client.force_login(user)

    url = reverse('business-profile-admin-collaborator-edit', kwargs={'sso_id': 1234})
    response = client.post(url, data={'action': action})

    assert response.status_code == 302
    assert response.url == reverse('business-profile-admin-tools')


@pytest.mark.parametrize('action', [forms.CHANGE_COLLABORATOR_TO_ADMIN])
def test_edit_collaborator_change_member_to_other(mock_collaborator_list, client, user, action):
    mock_collaborator_list.return_value = create_response(
        [
            {'sso_id': user.id, 'role': user_roles.ADMIN, 'company_email': user.email},
            {'sso_id': 1234, 'role': user_roles.MEMBER, 'company_email': 'jim@example.com'},
        ]
    )
    client.force_login(user)

    url = reverse('business-profile-admin-collaborator-edit', kwargs={'sso_id': 1234})
    response = client.post(url, data={'action': action})

    assert response.status_code == 302
    assert response.url == reverse('business-profile-admin-tools')


@pytest.mark.parametrize('action', [forms.CHANGE_COLLABORATOR_TO_MEMBER])
def test_edit_collaborator_change_admin_to_other(mock_collaborator_list, client, user, action):
    mock_collaborator_list.return_value = create_response(
        [
            {'sso_id': user.id, 'role': user_roles.ADMIN, 'company_email': user.email},
            {'sso_id': 1234, 'role': user_roles.ADMIN, 'company_email': 'jim@example.com'},
        ]
    )
    client.force_login(user)

    url = reverse('business-profile-admin-collaborator-edit', kwargs={'sso_id': 1234})
    response = client.post(url, data={'action': action})

    assert response.status_code == 302
    assert response.url == reverse('business-profile-admin-tools')


@mock.patch.object(api_client.company, 'collaborator_disconnect')
def test_edit_collaborator_edit_remove_collaborator(mock_collaborator_disconnect, client, user):
    client.force_login(user)

    mock_collaborator_disconnect.return_value = create_response()

    url = reverse('business-profile-admin-collaborator-edit', kwargs={'sso_id': 1234})

    response = client.post(url, data={'action': forms.REMOVE_COLLABORATOR})

    assert response.status_code == 302
    assert response.url == reverse('business-profile-admin-tools')
    assert mock_collaborator_disconnect.call_count == 1
    assert mock_collaborator_disconnect.call_args == mock.call(sso_session_id=user.session_id, sso_id=1234)


@mock.patch.object(api_client.supplier, 'disconnect_from_company')
def test_admin_disconnect_remote_validation_error(mock_disconnect_from_company, client, user):
    errors = ['Something went wrong']
    mock_disconnect_from_company.return_value = create_response(errors, status_code=400)
    client.force_login(user)

    url = reverse('business-profile-admin-disconnect')
    response = client.post(url)

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert response.context_data['form'].errors == {NON_FIELD_ERRORS: errors}


@mock.patch.object(api_client.supplier, 'disconnect_from_company')
def test_admin_disconnect_remote_error(mock_disconnect_from_company, client, user):
    mock_disconnect_from_company.return_value = create_response(status_code=500)
    client.force_login(user)

    url = reverse('business-profile-admin-disconnect')
    with pytest.raises(HTTPError):
        client.post(url)


@mock.patch.object(api_client.supplier, 'disconnect_from_company')
def test_admin_disconnect(mock_disconnect_from_company, client, user):
    mock_disconnect_from_company.return_value = create_response()
    client.force_login(user)

    url = reverse('business-profile-admin-disconnect')
    response = client.post(url)

    assert response.status_code == 302
    assert response.url == reverse('business-profile')
    assert mock_disconnect_from_company.call_count == 1
    assert mock_disconnect_from_company.call_args == mock.call(user.session_id)


@pytest.mark.parametrize('count,expected', ((1, True), (2, False)))
def test_admin_disconnect_is_sole_collaborator(mock_collaborator_list, count, expected, client, user):
    collaborators = [
        {'sso_id': user.id, 'role': user_roles.ADMIN, 'company_email': user.email},
        {'sso_id': 1234, 'role': user_roles.ADMIN, 'company_email': 'jim@example.com'},
    ]
    mock_collaborator_list.return_value = create_response(collaborators[:count])
    client.force_login(user)

    url = reverse('business-profile-admin-disconnect')
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['is_sole_admin'] is expected


def test_products_services_form_incorrect_value(client, user):
    client.force_login(user)

    url = reverse('business-profile-expertise-products-services', kwargs={'category': 'foo'})

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('business-profile-expertise-products-services-routing')


@mock.patch.object(api_client.company, 'collaborator_invite_create')
def test_admin_invite_administrator_remote_validation_error(mock_collaborator_invite_create, client, user):
    errors = ['Something went wrong']
    mock_collaborator_invite_create.return_value = create_response({'collaborator_email': errors}, status_code=400)
    client.force_login(user)

    url = reverse('business-profile-admin-invite-administrator')
    response = client.post(url, {'collaborator_email': 'jim@example.com'})

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert response.context_data['form'].errors == {NON_FIELD_ERRORS: errors}


@mock.patch.object(api_client.company, 'collaborator_invite_create')
def test_admin_invite_administrator_remote_error(mock_collaborator_invite_create, client, user):
    mock_collaborator_invite_create.return_value = create_response(status_code=500)
    client.force_login(user)

    url = reverse('business-profile-admin-invite-administrator')
    with pytest.raises(HTTPError):
        client.post(url, {'collaborator_email': 'jim@example.com'})


@mock.patch.object(api_client.company, 'collaborator_invite_create')
def test_admin_invite_administrator_new_collaborator(mock_collaborator_invite_create, client, user):
    mock_collaborator_invite_create.return_value = create_response(status_code=201)
    client.force_login(user)

    url = reverse('business-profile-admin-invite-administrator')
    response = client.post(url, {'collaborator_email': 'jim@example.com'})

    assert response.status_code == 302
    assert response.url == reverse('business-profile-admin-tools')
    assert mock_collaborator_invite_create.call_count == 1
    assert mock_collaborator_invite_create.call_args == mock.call(
        sso_session_id=user.session_id, data={'collaborator_email': 'jim@example.com', 'role': user_roles.ADMIN}
    )


def test_admin_invite_administrator_change_role(mock_collaborator_role_update, client, user, settings):
    client.force_login(user)

    url = reverse('business-profile-admin-invite-administrator')
    response = client.post(url, {'sso_id': '1234'})

    assert response.status_code == 302
    assert response.url == reverse('business-profile-admin-tools')
    assert mock_collaborator_role_update.call_count == 1
    assert mock_collaborator_role_update.call_args == mock.call(
        sso_session_id=user.session_id, sso_id='1234', role=user_roles.ADMIN
    )


@pytest.mark.parametrize(
    'url',
    (
        reverse('business-profile-admin-invite-administrator'),
        reverse('business-profile-admin-invite-collaborator'),
        reverse('business-profile-admin-collaborator-edit', kwargs={'sso_id': '123'}),
    ),
)
def test_admin_not_admin_role(mock_retrieve_supplier, client, user, url):
    mock_retrieve_supplier.return_value = create_response({'is_company_owner': False, 'role': user_roles.EDITOR})
    client.force_login(user)

    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith(reverse('business-profile'))


@pytest.mark.parametrize(
    'url',
    (
        reverse('business-profile-admin-invite-administrator'),
        reverse('business-profile-admin-invite-collaborator'),
        reverse('business-profile-admin-collaborator-edit', kwargs={'sso_id': '123'}),
        reverse('business-profile-admin-tools'),
        reverse('business-profile-admin-disconnect'),
    ),
)
def test_admin_anon_user(client, settings, url):
    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith(settings.LOGIN_URL)


@mock.patch.object(api_client.company, 'collaborator_invite_create')
def test_admin_invite_collaborator(mock_collaborator_invite_create, client, user):
    mock_collaborator_invite_create.return_value = create_response(status_code=201)
    client.force_login(user)

    url = reverse('business-profile-admin-invite-collaborator')
    response = client.post(url, {'collaborator_email': 'jim@example.com', 'role': user_roles.ADMIN})

    assert response.status_code == 302
    assert response.url == reverse('business-profile-admin-invite-collaborator')

    response = client.get(response.url)
    expected = 'We have sent a confirmation to jim@example.com with an invitation to become a collaborator'
    for message in response.context['messages']:
        assert str(message) == expected


@mock.patch.object(api_client.company, 'collaborator_invite_create')
def test_admin_invite_collaborator_remote_validation_error(mock_collaborator_invite_create, client, user):
    errors = {'collaborator_email': ['woe']}
    mock_collaborator_invite_create.return_value = create_response(errors, status_code=400)

    client.force_login(user)

    url = reverse('business-profile-admin-invite-collaborator')
    response = client.post(url, {'collaborator_email': 'jim@example.com', 'role': user_roles.ADMIN})

    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert response.context_data['form'].errors == errors


@mock.patch.object(api_client.company, 'collaborator_invite_create')
def test_admin_invite_collaborator_not_admin_remote_error(mock_collaborator_invite_create, client, user):
    mock_collaborator_invite_create.return_value = create_response(status_code=500)

    client.force_login(user)

    url = reverse('business-profile-admin-invite-collaborator')
    with pytest.raises(HTTPError):
        client.post(url, {'collaborator_email': 'jim@example.com', 'role': user_roles.ADMIN})


@mock.patch.object(api_client.company, 'collaborator_invite_delete')
def test_admin_collaborator_invite_delete(mock_collaborator_invite_delete, client, user):
    mock_collaborator_invite_delete.return_value = create_response()

    client.force_login(user)
    url = reverse('business-profile-collaboration-invite-delete')
    response = client.post(url, {'invite_key': '1234'})

    assert response.status_code == 302
    assert response.url == reverse('business-profile-admin-invite-collaborator')
    assert mock_collaborator_invite_delete.call_count == 1
    assert mock_collaborator_invite_delete.call_args == mock.call(sso_session_id=user.session_id, invite_key='1234')


@mock.patch.object(api_client.company, 'collaboration_request_accept')
def test_admin_collaboration_request_accept(mock_collaboration_request_accept, client, user):
    mock_collaboration_request_accept.return_value = create_response()
    admin_tools_url = reverse('business-profile-admin-tools')
    client.force_login(user)

    url = reverse('business-profile-admin-tools')
    response = client.post(url, {'request_key': '1234', 'action': forms.AdminCollaborationRequestManageForm.APPROVE})

    assert response.status_code == 302
    assert response.url == admin_tools_url
    assert mock_collaboration_request_accept.call_count == 1
    assert mock_collaboration_request_accept.call_args == mock.call(sso_session_id=user.session_id, request_key='1234')


@mock.patch.object(api_client.company, 'collaboration_request_delete')
def test_admin_collaboration_request_delete(mock_collaboration_request_delete, client, user):
    mock_collaboration_request_delete.return_value = create_response()
    admin_tools_url = reverse('business-profile-admin-tools')
    client.force_login(user)

    url = reverse('business-profile-admin-tools')
    response = client.post(url, {'request_key': '1234', 'action': forms.AdminCollaborationRequestManageForm.DELETE})

    assert response.status_code == 302
    assert response.url == admin_tools_url
    assert mock_collaboration_request_delete.call_count == 1
    assert mock_collaboration_request_delete.call_args == mock.call(sso_session_id=user.session_id, request_key='1234')


@mock.patch.object(api_client.company, 'collaboration_request_create')
def test_member_send_admin_request(mock_collaboration_request_create, client, user):
    mock_collaboration_request_create.return_value = create_response()

    client.force_login(user)

    response = client.post(reverse('business-profile'), {'action': forms.MemberCollaborationRequestForm.SEND_REQUEST})

    assert response.status_code == 302
    assert response.url == reverse('business-profile')

    assert mock_collaboration_request_create.call_count == 1
    assert mock_collaboration_request_create.call_args == mock.call(
        sso_session_id=user.session_id, role=user_roles.ADMIN
    )


@mock.patch.object(helpers, 'notify_company_admins_collaboration_request_reminder')
def test_member_send_admin_reminder(mock_collaboration_request_notify, client, user):
    mock_collaboration_request_notify.return_value = create_response()

    client.force_login(user)

    response = client.post(reverse('business-profile'), {'action': forms.MemberCollaborationRequestForm.SEND_REMINDER})

    assert response.status_code == 302
    assert response.url == reverse('business-profile')

    assert mock_collaboration_request_notify.call_count == 1
    assert mock_collaboration_request_notify.call_args == mock.call(
        email_data={
            'company_name': user.company.data['name'],
            'name': user.full_name,
            'email': user.email,
            'login_url': 'http://testserver/profile/business-profile/admin/',
        },
        form_url=reverse('business-profile'),
        sso_session_id=user.session_id,
    )


@mock.patch.object(api_client.company, 'collaboration_request_create')
def test_member_send_admin_request_error(mock_collaboration_request_create, client, user):
    mock_collaboration_request_create.return_value = create_response(status_code=500)
    client.force_login(user)

    url = reverse('business-profile')
    with pytest.raises(HTTPError):
        client.post(url, {'action': 'send_request'})


@mock.patch.object(api_client.company, 'collaboration_request_create')
def test_member_send_admin_request_error_400(mock_collaboration_request_create, client, user):
    errors = ['Something went wrong']
    mock_collaboration_request_create.return_value = create_response(errors, status_code=400)
    client.force_login(user)

    url = reverse('business-profile')
    response = client.post(url, {'action': 'send_request'})
    assert response.status_code == 200
    assert response.context_data['form'].is_valid() is False
    assert response.context_data['form'].errors == {NON_FIELD_ERRORS: errors}


def test_business_profile_member_redirect(client, user, mock_retrieve_supplier, company_profile_data):
    client.force_login(user)
    mock_retrieve_supplier.return_value = create_response({'role': user_roles.MEMBER})

    url = reverse('business-profile')
    response = client.get(url)

    context = response.context_data

    assert context['has_admin_request'] is True
    assert context['fab_tab_classes'] == 'active'
    assert context['contact_us_url'] == (urls.domestic.CONTACT_US / 'domestic')
    assert context['export_opportunities_apply_url'] == urls.domestic.EXPORT_OPPORTUNITIES
    assert context['is_profile_published'] == company_profile_data['is_published_find_a_supplier']
    assert context['FAB_BUSINESS_PROFILE_URL'] == (
        urls.international.TRADE_FAS / 'suppliers' / company_profile_data['number'] / company_profile_data['slug']
    )


def test_business_profile_member_no_company(client, user, mock_retrieve_supplier, mock_retrieve_company):
    client.force_login(user)
    mock_retrieve_supplier.return_value = create_response({'role': user_roles.MEMBER})
    mock_retrieve_company.return_value = create_response(status_code=404)

    url = reverse('business-profile')
    response = client.get(url)

    context = response.context_data

    assert 'has_admin_request' not in context
    assert context['fab_tab_classes'] == 'active'
    assert context['contact_us_url'] == (urls.domestic.CONTACT_US / 'domestic')
    assert context['export_opportunities_apply_url'] == urls.domestic.EXPORT_OPPORTUNITIES


def test_fab_redirect(client, user):
    client.force_login(user)

    url = '/profile/find-a-buyer/description/'
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == urls.domestic.SINGLE_SIGN_ON_PROFILE / 'business-profile/description'


def test_fab_redirect_landing(client, user):
    client.force_login(user)

    url = '/profile/find-a-buyer/'
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == urls.domestic.SINGLE_SIGN_ON_PROFILE / 'business-profile/'


def _check_template_use(response, template_name):
    for template in response.templates:
        if template.name == template_name:
            return

    assert False, f'Did not find template {template_name} in use in response'


@mock.patch.object(api_client.supplier, 'disconnect_from_company')
def test_business_user_disconnect(mock_disconnect_from_company, client, user):
    mock_disconnect_from_company.return_value = create_response()
    client.force_login(user)

    url = reverse('disconnect-account')

    # Quick check of GET
    response = client.get(url)
    _check_template_use(response, 'business_profile/disconnect-from-company.html')

    response = client.post(url, follow=True)

    assert mock_disconnect_from_company.call_count == 1
    assert mock_disconnect_from_company.call_args == mock.call(user.session_id)

    assert response.status_code == 200
    assert response.redirect_chain == [('/profile/business-profile/', 302)]
