from search import forms


def test_cleaned_form():
    form = forms.FeedbackForm(
        {
            'result_found': 'no',
            'search_target': 'Test',
            'reason_for_site_visit': 'Test',
            'from_search_query': 'hello',
            'from_search_page': 1,
            'contactable': 'yes',
            'contact_name': 'Test',
            'contact_email': 'test@example.com',
            'contact_number': '55512341234',
        }
    )
    form.is_valid()

    assert 'result_found' in form.serialized_data
    assert 'captcha' not in form.serialized_data
