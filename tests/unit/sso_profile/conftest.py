from io import BytesIO
from unittest import mock

import pytest
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from formtools.wizard.views import normalize_name
from PIL import Image, ImageDraw

from core.tests.helpers import create_response
from directory_constants import user_roles
from sso.helpers import api_client
from sso.models import BusinessSSOUser
from sso_profile.business_profile import views
from sso_profile.enrolment.helpers import ch_search_api_client
from .common.helpers import submit_step_factory

pytestmark = pytest.mark.django_db


def create_test_image(extension):
    image = Image.new('RGB', (300, 50))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), 'This text is drawn on image')
    byte_io = BytesIO()
    image.save(byte_io, extension)
    byte_io.seek(0)
    return byte_io


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()


@pytest.fixture
def sso_user_no_profile():
    return BusinessSSOUser(
        id=1,
        pk=1,
        email='jim@example.com',
        session_id='123',
        has_user_profile=False,
    )


@pytest.fixture
def sso_user_with_profile():
    return BusinessSSOUser(
        id=1,
        pk=1,
        email='jim2@example.com',
        session_id='123',
        has_user_profile=True,
        first_name='No Name',
    )


@pytest.fixture(autouse=True)
def sso_profile_feature_flags(settings):
    # solves this issue: https://github.com/pytest-dev/pytest-django/issues/601
    settings.SSO_PROFILE_FEATURE_FLAGS = {**settings.SSO_PROFILE_FEATURE_FLAGS}
    yield settings.SSO_PROFILE_FEATURE_FLAGS


@pytest.fixture(autouse=True)
def mock_create_user_profile():
    response = create_response(
        {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'job_title': 'Director',
            'mobile_phone_number': '08888888888',
        }
    )
    patch = mock.patch('directory_sso_api_client.sso_api_client.user.create_user_profile', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_update_user_profile():
    response = create_response()
    patch = mock.patch('directory_sso_api_client.sso_api_client.user.update_user_profile', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def update_supplier_profile_name():
    response = create_response()
    patch = mock.patch('directory_api_client.api_client.supplier.profile_update', return_value=response)
    yield patch.start()
    patch.stop()


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
def not_publishable_company_profile_data():
    return {
        'name': 'Cool Company',
        'is_publishable': False,
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
        return_value=create_response(
            {
                'is_company_owner': True,
                'role': user_roles.ADMIN,
            }
        ),
    )
    yield patch.start()
    patch.stop()


@pytest.fixture
def mock_retrieve_member_supplier():
    patch = mock.patch.object(
        api_client.supplier,
        'retrieve_profile',
        return_value=create_response(
            {
                'role': user_roles.MEMBER,
            }
        ),
    )
    yield patch.start()
    patch.stop()


@pytest.fixture
def mock_get_companies_house_profile():
    patch = mock.patch.object(
        ch_search_api_client.company,
        'get_company_profile',
        return_value=create_response(
            {
                'company_number': '12345678',
                'company_name': 'Example corp',
                'sic_codes': ['1234'],
                'date_of_creation': '2001-01-20',
                'registered_office_address': {'one': '555', 'two': 'fake street'},
            }
        ),
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
        client=client, url_name='sso_profile:business-profile-case-study', view_class=views.CaseStudyWizardCreateView
    )


@pytest.fixture
def submit_case_study_edit_step(client):
    url_name = 'sso_profile:business-profile-case-study-edit'
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
