from directory_api_client import api_client


def get_user_products(sso_session_id):
    results = api_client.personalisation.get_user_products(sso_session_id)
    if results.status_code == 200:
        return results.json()
    return []


def add_update_user_product(sso_session_id, product_data):
    results = api_client.personalisation.add_update_user_product(sso_session_id, product_data)
    return results.json()
