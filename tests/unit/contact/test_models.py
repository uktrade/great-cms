import pytest

from contact.models import ContactSuccessSnippet, ContactUsGuidanceSnippet
from core import snippet_slugs
from core.cms_snippets import NonPageContentSnippetBase


def test_non_page_content_snippet_base_no_slug_options():
    class TestModelWithNoSlugOptions(NonPageContentSnippetBase):
        class Meta:
            app_label = 'contact'

    test_instance_no_slug_options = TestModelWithNoSlugOptions()
    assert test_instance_no_slug_options.slug_options == {}

    with pytest.raises(NotImplementedError) as exc_info:
        test_instance_no_slug_options.save()

    assert exc_info.value.args[0] == 'The subclass must have slug_options defined.'


def test_contact_success_snippet_no_slug_set():
    # This test confirms behaviour in the NonPageContentSnippetBase superclass
    snippet = ContactSuccessSnippet()

    assert not snippet.slug
    with pytest.raises(NotImplementedError) as exc_info:
        snippet.save()

    assert exc_info.value.args[0] == 'The subclass must set a value for self.slug before during save()'


@pytest.mark.django_db
def test_contact_slug_options_are_set():
    snippet = ContactSuccessSnippet()
    slug_field = snippet._meta.get_field('slug')
    assert len(slug_field.choices) > 1


@pytest.mark.parametrize(
    'model_class,slug,expected_str',
    (
        (
            ContactSuccessSnippet,
            snippet_slugs.HELP_FORM_SUCCESS,
            'Contact Success Snippet: Contact domestic form success page content',
        ),
        (
            ContactUsGuidanceSnippet,
            snippet_slugs.HELP_ACCOUNT_COMPANY_NOT_FOUND,
            'Contact Us Guidance Snippet: Guidance - Company not found',
        ),
    ),
)
@pytest.mark.django_db
def test_contact_snippet_save_and_str(model_class, slug, expected_str):
    snippet = model_class(slug=slug)
    snippet.save()
    snippet.refresh_from_db()
    assert f'{snippet}' == expected_str
