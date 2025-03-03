import requests


def get_postcode_data(postcode):
    response = requests.get(f'https://api.postcodes.io/postcodes/{postcode}', timeout=4)
    response.raise_for_status()
    data = response.json()

    return data


def get_dbt_news_articles():
    response = requests.get(
        'https://www.gov.uk/api/content/government/organisations/department-for-business-and-trade', timeout=4
    )
    response.raise_for_status()
    data = response.json()

    news_articles = data.get('details').get('ordered_featured_documents')

    return news_articles[:3]


def get_nearest_growth_hub_by_postode(postcode):
    return {
        'title': 'The Growth Hub',
        'distance': f'1.2 miles from {postcode}',
        'address': 'Street name, Town/City, County, Postcode',
        'email': 'growthhub@mail.com',
    }
