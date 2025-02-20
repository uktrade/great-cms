import requests


def get_postcode_data(postcode):
    response = requests.get(f'https://api.postcodes.io/postcodes/{postcode}', timeout=4)
    response.raise_for_status()
    data = response.json()

    return data
