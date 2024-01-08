from international_online_offer.models import get_user_data_for_user


def eyb_user(request):
    user = get_user_data_for_user(request)
    if not user:
        return {}
    else:
        return {'eyb_user': user}


def feedback_next_url(request):
    return {'feedback_next_url': request.build_absolute_uri()}
