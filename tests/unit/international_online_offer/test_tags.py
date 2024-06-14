import pytest

import international_online_offer.templatetags.eyb_tags as eyb_tags


@pytest.mark.parametrize(
    'context_data,expected',
    (
        (
            {'entry_salary': 1, 'mid_salary': 2, 'executive_salary': 3},
            {'parent_column_class': 'govuk-grid-column-full', 'salary_card_class': 'govuk-grid-column-one-third'},
        ),
        (
            {'entry_salary': 1, 'mid_salary': 2, 'executive_salary': None},
            {'parent_column_class': 'govuk-grid-column-two-thirds', 'salary_card_class': 'govuk-grid-column-one-half'},
        ),
    ),
)
def test_get_salary_display_classes(context_data, expected):
    display_classes = eyb_tags.get_salary_display_classes(context_data)
    assert display_classes == expected
