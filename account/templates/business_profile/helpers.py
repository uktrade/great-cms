import http

import directory_components.helpers
from directory_api_client.client import api_client
from directory_constants import company_types, user_roles
from directory_forms_api_client import actions
from django.conf import settings

from core.helpers import get_company_admins


def get_company_profile(sso_session_id):
    response = api_client.company.profile_retrieve(sso_session_id)
    if response.status_code == http.client.NOT_FOUND:
        return None
    response.raise_for_status()
    return response.json()


def get_supplier_profile(sso_id):
    response = api_client.supplier.retrieve_profile(sso_id)
    if response.status_code == http.client.NOT_FOUND:
        return None
    response.raise_for_status()
    return response.json()


class CompanyParser(directory_components.helpers.CompanyParser):
    @property
    def is_in_companies_house(self):
        return self.data.get('company_type') == company_types.COMPANIES_HOUSE

    @property
    def is_identity_check_message_sent(self):
        return self.data['is_identity_check_message_sent']

    def serialize_for_template(self):
        if not self.data:
            return {}
        return {
            **self.data,
            'date_of_creation': self.date_of_creation,
            'address': self.address,
            'sectors': self.sectors_label,
            'keywords': self.keywords,
            'employees': self.employees_label,
            'expertise_industries': self.expertise_industries_label,
            'expertise_regions': self.expertise_regions_label,
            'expertise_countries': self.expertise_countries_label,
            'expertise_languages': self.expertise_languages_label,
            'has_expertise': self.has_expertise,
            'expertise_products_services': self.expertise_products_services_label,
            'is_in_companies_house': self.is_in_companies_house,
        }

    def serialize_for_form(self):
        if not self.data:
            return {}
        return {**self.data, 'date_of_creation': self.date_of_creation, 'address': self.address}


def collaborator_list(sso_session_id):
    response = api_client.company.collaborator_list(sso_session_id=sso_session_id)
    response.raise_for_status()
    return response.json()


def retrieve_collaborator(sso_session_id, collaborator_sso_id):
    for collaborator in collaborator_list(sso_session_id):
        if collaborator['sso_id'] == collaborator_sso_id:
            return collaborator


def remove_collaborator(sso_session_id, sso_id):
    response = api_client.company.collaborator_disconnect(sso_session_id=sso_session_id, sso_id=sso_id)
    response.raise_for_status()
    assert response.status_code == 200


def disconnect_from_company(sso_session_id):
    response = api_client.supplier.disconnect_from_company(sso_session_id)
    response.raise_for_status()
    assert response.status_code == 200


def is_sole_admin(sso_session_id):
    collaborators = collaborator_list(sso_session_id)
    return [collaborator['role'] for collaborator in collaborators].count(user_roles.ADMIN) == 1


def collaborator_invite_create(sso_session_id, collaborator_email, role):
    data = {'collaborator_email': collaborator_email, 'role': role}
    response = api_client.company.collaborator_invite_create(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()


def collaborator_invite_list(sso_session_id):
    response = api_client.company.collaborator_invite_list(sso_session_id=sso_session_id)
    response.raise_for_status()
    return response.json()


def collaborator_invite_delete(sso_session_id, invite_key):
    response = api_client.company.collaborator_invite_delete(sso_session_id=sso_session_id, invite_key=invite_key)
    response.raise_for_status()


def collaborator_role_update(sso_session_id, sso_id, role):
    response = api_client.company.collaborator_role_update(sso_session_id=sso_session_id, sso_id=sso_id, role=role)
    response.raise_for_status()


def collaboration_request_list(sso_session_id):
    response = api_client.company.collaboration_request_list(sso_session_id=sso_session_id)
    response.raise_for_status()
    return response.json()


def collaboration_request_accept(sso_session_id, request_key):
    response = api_client.company.collaboration_request_accept(sso_session_id=sso_session_id, request_key=request_key)
    response.raise_for_status()


def collaboration_request_delete(sso_session_id, request_key):
    response = api_client.company.collaboration_request_delete(sso_session_id=sso_session_id, request_key=request_key)
    response.raise_for_status()


def collaboration_request_create(sso_session_id, role):
    response = api_client.company.collaboration_request_create(sso_session_id=sso_session_id, role=role)
    response.raise_for_status()


def has_editor_admin_request(sso_session_id, sso_id):
    collaboration_requests = collaboration_request_list(sso_session_id)
    return bool([r for r in collaboration_requests if r['requestor_sso_id'] == sso_id and not r['accepted']])


def notify_company_admins_collaboration_request_reminder(sso_session_id, email_data, form_url):

    company_admins = get_company_admins(sso_session_id)
    assert company_admins, f"No admin found for {email_data['company_name']}"
    for admin in company_admins:
        action = actions.GovNotifyEmailAction(
            email_address=admin['company_email'],
            template_id=settings.GOV_NOTIFY_COLLABORATION_REQUEST_RESENT,
            form_url=form_url,
        )
        response = action.save(email_data)
        response.raise_for_status()
