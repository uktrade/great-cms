import pytest

from tests.unit.core import factories

from cms_extras.modeladmin import CaseStudyAdmin


@pytest.mark.django_db
def test_case_study_modeladmin_list_display_methods():
    admin = CaseStudyAdmin()
    obj = factories.CaseStudyFactory()

    obj.country_code_tags.add('Europe', 'FR')
    obj.hs_code_tags.add('HS1234', 'HS123456')

    assert sorted(admin.associated_country_code_tags(obj)) == ['Europe', 'FR']
    assert sorted(admin.associated_hs_code_tags(obj)) == ['HS1234', 'HS123456']
