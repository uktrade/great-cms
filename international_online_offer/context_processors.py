from django.urls import reverse_lazy

from international_online_offer.core.helpers import (
    is_triage_complete as is_triage_complete_helper,
)
from international_online_offer.models import (
    get_triage_data_for_user,
    get_user_data_for_user,
)


def eyb_user(request):
    user = get_user_data_for_user(request)
    if not user:
        return {}
    else:
        return {'eyb_user': user}


def feedback_next_url(request):
    return {'feedback_next_url': request.build_absolute_uri(request.path)}


def is_using_triage(request):
    current_url = request.build_absolute_uri(request.path)
    business_headquarters = str(reverse_lazy('international_online_offer:business-headquarters'))
    find_your_company = str(reverse_lazy('international_online_offer:find-your-company'))
    business_sector = str(reverse_lazy('international_online_offer:business-sector'))
    business_details = str(reverse_lazy('international_online_offer:company-details'))
    contact_details = str(reverse_lazy('international_online_offer:contact-details'))
    when_want_setup = str(reverse_lazy('international_online_offer:when-want-setup'))
    about_your_business = str(reverse_lazy('international_online_offer:about-your-business'))
    know_setup_location = str(reverse_lazy('international_online_offer:know-setup-location'))
    intent_url = str(reverse_lazy('international_online_offer:intent'))
    location_url = str(reverse_lazy('international_online_offer:location'))
    hiring_url = str(reverse_lazy('international_online_offer:hiring'))
    spend_url = str(reverse_lazy('international_online_offer:spend'))
    triage_urls = [
        business_headquarters,
        business_sector,
        find_your_company,
        business_details,
        contact_details,
        when_want_setup,
        about_your_business,
        know_setup_location,
        intent_url,
        location_url,
        hiring_url,
        spend_url,
    ]
    for url in triage_urls:
        if url in current_url:
            return True


def is_using_login(request):
    current_url = request.build_absolute_uri(request.path)
    signup_url = str(reverse_lazy('international_online_offer:signup'))
    login_url = str(reverse_lazy('international_online_offer:login'))
    user_flow_urls = [signup_url, login_url]
    for url in user_flow_urls:
        if url in current_url:
            return True
    return False


# Function defined to assert if a user is in a EYB transactional flow e.g. the triage
def hide_primary_nav(request):
    hide_primary_nav = is_using_triage(request) or is_using_login(request)
    return {'hide_primary_nav': hide_primary_nav}


def is_triage_complete(request):
    triage_complete = is_triage_complete_helper(get_user_data_for_user(request), get_triage_data_for_user(request))
    return {'is_triage_complete': triage_complete}
