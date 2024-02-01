from django.urls import reverse_lazy

from international_online_offer.models import get_user_data_for_user


def eyb_user(request):
    user = get_user_data_for_user(request)
    if not user:
        return {}
    else:
        return {'eyb_user': user}


def feedback_next_url(request):
    return {'feedback_next_url': request.build_absolute_uri()}


def is_using_triage(request):
    current_url = request.build_absolute_uri()
    sector_url = str(reverse_lazy('international_online_offer:sector'))
    intent_url = str(reverse_lazy('international_online_offer:intent'))
    location_url = str(reverse_lazy('international_online_offer:location'))
    hiring_url = str(reverse_lazy('international_online_offer:hiring'))
    spend_url = str(reverse_lazy('international_online_offer:spend'))
    triage_urls = [sector_url, intent_url, location_url, hiring_url, spend_url]
    for url in triage_urls:
        if url in current_url:
            return True
    return False


def is_using_login_or_profile(request):
    current_url = request.build_absolute_uri()
    signup_url = str(reverse_lazy('international_online_offer:signup'))
    login_url = str(reverse_lazy('international_online_offer:login'))
    profile_url = str(reverse_lazy('international_online_offer:profile'))
    user_flow_urls = [signup_url, login_url, profile_url]
    for url in user_flow_urls:
        if url in current_url:
            return True
    return False


def hide_primary_nav(request):
    hide_primary_nav = is_using_triage(request) or is_using_login_or_profile(request)
    return {'hide_primary_nav': hide_primary_nav} 