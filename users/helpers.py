from directory_api_client import api_client


def get_user_products(sso_session_id):
    results = api_client.personalisation.get_user_products(sso_session_id)
    return results.json() if results.status_code == 200 else []


def add_update_user_product(sso_session_id, product_data):
    results = api_client.personalisation.add_update_user_product(sso_session_id, product_data)
    return results.json()


def get_user_markets(sso_session_id):
    results = api_client.personalisation.get_user_markets(sso_session_id)
    return results.json() if results.status_code == 200 else []


def add_update_user_market(sso_session_id, market_data):
    results = api_client.personalisation.add_update_user_market(sso_session_id, market_data)
    return results.json()
