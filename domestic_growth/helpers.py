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
