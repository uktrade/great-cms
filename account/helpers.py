from directory_api_client.client import api_client
from directory_constants import user_roles
from directory_sso_api_client import sso_api_client


def create_user_profile(sso_session_id, data):
    profile_response = sso_api_client.user.create_user_profile(sso_session_id=sso_session_id, data=data)
    profile_response.raise_for_status()
    # Call made to Supplier to keep name in Sync
    # To be removed once we remove from supplier model
    update_supplier_profile_name(sso_session_id=sso_session_id, data=data)
    return profile_response


def update_user_profile(sso_session_id, data):
    profile_response = sso_api_client.user.update_user_profile(sso_session_id=sso_session_id, data=data)
    profile_response.raise_for_status()
    # Call made to Supplier to keep name in Sync
    # To be removed once we remove from supplier model
    update_supplier_profile_name(sso_session_id=sso_session_id, data=data)
    return profile_response


def update_supplier_profile_name(sso_session_id, data):
    name = extract_full_name(data)
    response = api_client.supplier.profile_update(sso_session_id=sso_session_id, data={'name': name})
    if response.status_code not in [200, 404]:
        response.raise_for_status()
    return response


def extract_full_name(data):
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    return f'{first_name} {last_name}'


def get_company_admins(sso_session_id):
    response = api_client.company.collaborator_list(sso_session_id=sso_session_id)
    response.raise_for_status()

    collaborators = response.json()
    return [collaborator for collaborator in collaborators if collaborator['role'] == user_roles.ADMIN]