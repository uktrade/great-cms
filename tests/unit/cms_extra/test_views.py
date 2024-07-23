import pytest
from django.http import StreamingHttpResponse
from django.urls import reverse

from cms_extras.modeladmin import CaseStudyAdmin
from tests.unit.core.factories import CaseStudyFactory


@pytest.mark.django_db
def test_case_study_view(client, django_user_model, mock_opensearch_get_connection):
    user = django_user_model.objects.create_user(
        username='username',
        password='password',
        is_staff=True,
    )
    client.login(username='username', password='password')

    assert user.is_authenticated and user.is_active and user.is_staff

    case_study = CaseStudyFactory()

    url = reverse('cms_extras:case-study-view', args=[case_study.id])
    resp = client.get(url)

    assert resp.status_code == 200
    assert resp.context['case_study'] == case_study
    assert resp.context['backlink'] == '/admin/core/casestudy/'


@pytest.mark.django_db
@pytest.mark.parametrize('is_staff', (True, False))
def test_case_study_view__access(django_user_model, client, is_staff):
    user = django_user_model.objects.create_user(
        username='username',
        password='password',
    )
    user.is_staff = is_staff
    user.save()

    client.login(username='username', password='password')

    assert user.is_authenticated and user.is_active and user.is_staff == is_staff

    case_study = CaseStudyFactory()

    url = reverse('cms_extras:case-study-view', args=[case_study.id])
    resp = client.get(url)

    if is_staff:
        assert resp.status_code == 200
    else:
        assert resp.status_code == 302
        assert resp.headers['location'] == f'/django-admin/login/?next=/admin/cms-extras/case-study/{case_study.id}/'


@pytest.mark.django_db
def test_case_study_admin_view(client, django_user_model, mock_opensearch_get_connection):
    user = django_user_model.objects.create_user(
        username='username', password='password', is_staff=True, is_superuser=True
    )
    client.login(username='username', password='password')

    assert user.is_authenticated and user.is_active and user.is_staff and user.is_superuser

    case_study = CaseStudyFactory()
    case_study.country_code_tags.add('FR')
    case_study.save()

    url = CaseStudyAdmin().url_helper.index_url
    resp = client.get(url)

    assert resp.status_code == 200
    assert 'Download CSV' in str(resp.content)

    csv_url = url + '?export=csv'
    csv_resp = client.get(csv_url)

    assert isinstance(csv_resp, StreamingHttpResponse)

    response = [item.decode('utf-8') for item in csv_resp.streaming_content]
    list_response = [item.split('\r\n') for item in response if item]

    csv_header = [item.split(',') for item in filter(None, list_response[0])][0]

    content_rows = [item.split(',') for item in filter(None, list_response[1])]

    assert csv_header == ['Internal Case Study Title', 'Summary Context', 'Lead Title', 'Association', 'Attribute']
    assert content_rows[0][3] == 'associated_country_code_tags'
    assert content_rows[0][4] == 'FR'
