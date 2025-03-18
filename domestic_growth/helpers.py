from directory_api_client import api_client


def get_local_support_by_postcode(postcode):
    postcode = postcode.replace(' ', '')

    response = api_client.dataservices.get_local_support_by_postcode(postcode=postcode)

    response.raise_for_status()
    data = response.json()

    return data


def get_postcode_data(postcode):

    if not postcode:
        return None

    return {
        'in_england': 'true',
        'in_london': 'false',
        'region': 'North Yorkshire',
        'growth_hubs': [
            {
                'id': 40,
                'name': 'York and North Yorkshire Growth Hub',
                'description': 'The growth hub provides support via a web portal signposting business owners.',
                'contacts': {
                    'id': 40,
                    'website': 'https://www.ynygrowthhub.com/',
                    'phone': 'tel:+44-800-246-5045',
                    'email': 'support@ynygrowthhub.com',
                },
                'boundary_name': 'York',
                'boundary_type': 'local authority district',
                'boundary_level': '1',
            }
        ],
        'chambers_of_commerce': [
            {
                'id': 21,
                'name': 'Cornwall Chamber of Commerce',
                'contacts': {
                    'id': 61,
                    'website': 'https://www.britishchambers.org.uk/locations/cornwall-chamber-of-commerce/',
                    'phone': 'tel:+44-1209-216006',
                    'email': 'hello@cornwallchamber.co.uk',
                },
                'place': {
                    'id': 21,
                    'address': 'Cardrew Way, Redruth TR15 1SP, UK',
                    'postcode': 'TR15 1SP',
                    'latitude': '50.2396049',
                    'longitude': '-5.2235327',
                    'northings': '170243.95863256758',
                    'eastings': '42708.86982457701',
                },
                'distance': 503844.704398452,
            },
            {
                'id': 20,
                'name': 'Devon & Plymouth Chamber of Commerce',
                'contacts': {
                    'id': 60,
                    'website': 'https://www.britishchambers.org.uk/locations/devon-plymouth-chamber-of-commerce/',
                    'phone': 'tel:+44-1752-220471',
                    'email': 'reception@devonchamber.co.uk',
                },
                'place': {
                    'id': 20,
                    'address': 'Unit 5, Derriford Business Park, Derriford Rd, Plymouth PL6 5QZ, UK',
                    'postcode': 'PL6 5QZ',
                    'latitude': '50.4159241',
                    'longitude': '-4.123827',
                    'northings': '249209.0072775367',
                    'eastings': '59497.46054802963',
                },
                'distance': 449265.111132264,
            },
            {
                'id': 31,
                'name': 'Inverness Chamber of Commerce',
                'contacts': {
                    'id': 71,
                    'website': 'https://www.britishchambers.org.uk/locations/inverness-chamber-of-commerce/',
                    'phone': 'tel:+44-1463-718131',
                    'email': 'info@inverness-chamber.co.uk',
                },
                'place': {
                    'id': 31,
                    'address': 'Metropolitan House, 31-33 High St, Inverness IV1 1HT, UK',
                    'postcode': 'IV1 1HT',
                    'latitude': '57.4779854',
                    'longitude': '-4.2242293',
                    'northings': '266729.03569369053',
                    'eastings': '845266.9326259879',
                },
                'distance': 427245.039668557,
            },
            {
                'id': 28,
                'name': 'Isle of Wight Chamber of Commerce, Tourism and Industry',
                'contacts': {
                    'id': 68,
                    'website': 'https://www.britishchambers.org.uk/locations/isle-of-wight-chamber-of-commerce/',
                    'phone': 'tel:+44-1983-520777',
                    'email': 'chamber@iwchamber.co.uk',
                },
                'place': {
                    'id': 28,
                    'address': 'Branstone, Sandown PO36 0LT, UK',
                    'postcode': 'PO36 0LT',
                    'latitude': '50.6506157',
                    'longitude': '-1.216747',
                    'northings': '455469.1799838217',
                    'eastings': '83730.85454834852',
                },
                'distance': 376619.135441751,
            },
            {
                'id': 19,
                'name': 'Dorset Chamber of Commerce & Industry',
                'contacts': {
                    'id': 59,
                    'website': 'https://www.britishchambers.org.uk/locations/dorset-chamber-of-commerce-and-industry/',
                    'phone': 'tel:+44-1202-714800',
                    'email': 'contact@dorsetchamber.co.uk',
                },
                'place': {
                    'id': 19,
                    'address': 'Ling Rd, Poole BH12 4NZ, UK',
                    'postcode': 'BH12 4NZ',
                    'latitude': '50.7449989',
                    'longitude': '-1.9518259',
                    'northings': '403494.7417052327',
                    'eastings': '93934.84516557035',
                },
                'distance': 369611.173494856,
            },
        ],
    }


def get_dbt_news_articles():
    response = api_client.dataservices.get_news_content()
    response.raise_for_status()
    data = response.json()

    return data[:3]
