from find_a_buyer import helpers


def test_build_company_address():
    company_profile = {
        'address_line_1': '123 fake street',
        'address_line_2': '',
        'locality': 'London',
        'country': 'UK',
        'postal_code': 'E14 9OX',
        'po_box': '',
    }

    assert helpers.build_company_address(company_profile) == ('123 fake street, London, UK, E14 9OX')
