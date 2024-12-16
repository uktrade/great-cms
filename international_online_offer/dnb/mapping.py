def extract_address(address_data):
    """Extract address fields from API response"""

    return {
        **_get_address_line(address_data),
        'address_town': address_data.get('addressLocality', {}).get('name', ''),
        'address_county': address_data.get('addressCounty', {}).get('name', ''),
        'address_postcode': address_data.get('postalCode', ''),
        'address_country': address_data.get('addressCountry', {}).get('isoAlpha2Code', ''),
    }


def _get_address_line(address_data):
    """Extract address line fields from streetAddress field"""

    street_address = address_data.get('streetAddress', {})
    if isinstance(street_address, dict):
        return {
            'address_line_1': street_address.get('line1', ''),
            'address_line_2': street_address.get('line2', ''),
        }
    else:
        return {
            'address_line_1': '',
            'address_line_2': '',
        }


def _get_registered_address_line(address_data):
    """Extract address line fields from streetName"""

    street_name = address_data.get('streetName', '')
    if street_name and isinstance(address_data.get('streetName'), str):
        address_line = [a.strip() for a in address_data['streetName'].split(',')]
        return {
            'address_line_1': address_line[0],
            'address_line_2': address_line[1] if len(address_line) > 1 else '',
        }
    else:
        return {}


def extract_registered_address(company_data):
    if company_data['organization']['primaryAddress'].get('isRegisteredAddress', False):
        address = extract_address(company_data['organization']['primaryAddress'])
    elif 'registeredAddress' not in company_data['organization']:
        address = {}
    else:
        address_data = company_data['organization']['registeredAddress']
        address = extract_address(address_data)
        # Updated registered address line fields with streetName.
        # If streetName is empty or not present the address line mapped
        # from streetAddress will persist
        address.update(_get_registered_address_line(address_data))

    return {f'registered_{field}': value for field, value in address.items()}


def extract_trading_names(company_data):
    trading_names = company_data['organization'].get('tradeStyleNames', [])

    return [item['name'] for item in trading_names]


def extract_company_data(company_data):
    company = {
        'duns_number': company_data['organization']['duns'],
        'primary_name': company_data['organization']['primaryName'],
        'trading_names': extract_trading_names(company_data),
        'global_ultimate_duns_number': company_data['organization']['corporateLinkage']
        .get('globalUltimate', {})
        .get('duns', ''),
        'global_ultimate_primary_name': company_data['organization']['corporateLinkage']
        .get('globalUltimate', {})
        .get('primaryName', ''),
        'domain': company_data['organization'].get('domain', ''),
        **extract_address(company_data['organization']['primaryAddress']),
    }

    return company
