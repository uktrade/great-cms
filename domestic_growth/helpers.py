import requests
from directory_api_client import api_client


def get_postcode_data(postcode):
    response = requests.get(f'https://api.postcodes.io/postcodes/{postcode}', timeout=4)
    response.raise_for_status()
    data = response.json()

    return data


def get_dbt_news_articles():
    response = api_client.dataservices.get_news_content()
    response.raise_for_status()
    data = response.json()

    return data[:3]
