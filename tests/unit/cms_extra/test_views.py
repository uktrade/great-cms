import pytest

from django.urls import reverse

from tests.unit.core.factories import CaseStudyFactory


@pytest.mark.django_db
def test_case_study_view(client, django_user_model):

    user = django_user_model.objects.create_user(
        username='username',
        password='password',
        is_staff=True
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
        assert resp._headers['location'][1] == f'/django-admin/login/?next=/cms-extras/case-study/{case_study.id}/'
