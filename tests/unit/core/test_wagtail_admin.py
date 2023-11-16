from wagtail.admin.forms import WagtailAdminPageForm

from core.models import DetailPage


def test_detail_page_custom_edit_handler():
    edit_handler = DetailPage.get_edit_handler()
    detail_page_form = edit_handler.get_form_class()

    assert (issubclass(detail_page_form, WagtailAdminPageForm)) is True
    assert len(edit_handler.children) == 4
    assert edit_handler.children[0].heading == 'Content'
    assert edit_handler.children[1].heading == 'Layout'
    assert edit_handler.children[2].heading == 'SEO'
    assert edit_handler.children[3].heading == 'Settings'
