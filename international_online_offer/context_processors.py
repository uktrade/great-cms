from international_online_offer.models import get_user_data


def eyb_user(request):
    if hasattr(request, 'user'):
        if hasattr(request.user, 'hashed_uuid'):
            eyb_user = get_user_data(request.user.hashed_uuid)
            return {'eyb_user': eyb_user}
    return {}


def feedback_next_url(request):
    return {'feedback_next_url': request.build_absolute_uri()}
