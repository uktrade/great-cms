import pytest

from contact import snippet_slugs
from contact.models import ContactSuccessSnippet
from core.cms_snippets import NonPageContentSnippetBase


def test_non_page_content_snippet_base_not_implemented_errors():
    class TestModelWithNoSlugField(NonPageContentSnippetBase):
        class Meta:
            app_label = 'contact'

    test_instance_no_slug_field = TestModelWithNoSlugField()

    with pytest.raises(NotImplementedError) as exc_info:
        test_instance_no_slug_field.save()

    assert exc_info.value.args[0] == 'The subclass must have a slug field.'


def test_contact_success_snippet_no_slug_set():
    # This test confirms behaviour in the NonPageContentSnippetBase superclass
    snippet = ContactSuccessSnippet()

    assert not snippet.slug
    with pytest.raises(NotImplementedError) as exc_info:
        snippet.save()

    assert exc_info.value.args[0] == 'The subclass must set a value for self.slug before during save()'


@pytest.mark.django_db
def test_contact_success_snippet_save():
    snippet = ContactSuccessSnippet(slug=snippet_slugs.HELP_FORM_SUCCESS)
    snippet.save()
    snippet.refresh_from_db()
    assert f'{snippet}' == 'Contact Success Snippet: Contact domestic form success'
