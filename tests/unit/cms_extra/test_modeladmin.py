from unittest import mock

import pytest

from cms_extras.modeladmin import CaseStudyAdmin, CaseStudyAdminButtonHelper
from core.models import CaseStudy, CaseStudyRelatedPages
from tests.unit.core import factories


@pytest.mark.django_db
def test_case_study_modeladmin_list_display_methods():
    admin = CaseStudyAdmin()
    obj = factories.CaseStudyFactory()
    detail_page = factories.DetailPageFactory()
    topic_page = factories.TopicPageFactory()
    module_page = factories.CuratedListPageFactory()

    obj.country_code_tags.add('Europe', 'FR')
    obj.hs_code_tags.add('HS1234', 'HS123456')

    # Adding related pages to case study
    CaseStudyRelatedPages.objects.create(page=detail_page, case_study=obj)
    CaseStudyRelatedPages.objects.create(page=topic_page, case_study=obj)
    CaseStudyRelatedPages.objects.create(page=module_page, case_study=obj)

    assert sorted(admin.associated_country_code_tags(obj)) == ['Europe', 'FR']
    assert sorted(admin.associated_hs_code_tags(obj)) == ['HS1234', 'HS123456']
    assert (
        admin.get_related_pages(obj)
        == '<strong>LESSON: </strong> Detail page<br><strong>TOPIC: </strong> Topic page<br><strong>MODULE: </strong> Curated List Page<br>'  # noqa
    )


@pytest.mark.django_db
def test_casestudyadminbuttonhelper(rf, django_user_model):

    obj = factories.CaseStudyFactory()

    user = django_user_model.objects.create_user(username='username', password='password', is_staff=True)

    mock_request = rf.get('/')
    mock_request.user = user

    mock_view = mock.Mock(name='mock_view')
    mock_view.model = CaseStudy
    mock_view.url_helper.get_action_url.return_value = '/admin/mock-url/path/'

    helper = CaseStudyAdminButtonHelper(
        request=mock_request,
        view=mock_view,
    )

    assert helper.view_button(obj) == {
        'classname': 'button button-small icon icon-doc',
        'label': 'View case study',
        'title': 'View case study',
        'url': f'/admin/cms-extras/case-study/{obj.id}/',
    }

    assert helper.get_buttons_for_obj(obj) == [
        {'classname': 'button', 'label': 'Inspect', 'title': 'Inspect this case study', 'url': '/admin/mock-url/path/'},
        {'classname': 'button', 'label': 'Edit', 'title': 'Edit this case study', 'url': '/admin/mock-url/path/'},
        {
            'classname': 'button no',
            'label': 'Delete',
            'title': 'Delete this case study',
            'url': '/admin/mock-url/path/',
        },
        {
            'classname': 'button button-small icon icon-doc',
            'label': 'View case study',
            'title': 'View case study',
            'url': f'/admin/cms-extras/case-study/{obj.id}/',
        },
    ]
