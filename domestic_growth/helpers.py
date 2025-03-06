import requests


def get_dbt_news_articles():
    response = requests.get(
        'https://www.gov.uk/api/content/government/organisations/department-for-business-and-trade', timeout=4
    )
    response.raise_for_status()
    data = response.json()

    news_articles = data.get('details').get('ordered_featured_documents')

    return news_articles[:3]


def get_nearest_by_postcode(postcode):
    return {
        'growth_hub': {
            'title': 'The Growth Hub',
            'distance': f'1.2 miles from {postcode}',
            'address': 'Street name, Town/City, County, Postcode',
            'email': 'growthhub@mail.com',
        },
        'chamber_of_commerce': {
            'title': 'The Commerce Chamber',
            'address': f'Commerce Street, Chambering, {postcode}',
            'email': 'chamber_of_commerce@mail.com',
        },
    }
