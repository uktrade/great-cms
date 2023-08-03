from international_online_offer.models import UserData


def eyb_user(request):
    if request.user.is_authenticated:
        return {'eyb_user': UserData.objects.filter(hashed_uuid=request.user.hashed_uuid).first()}
    return {}


def feedback_next_url(request):
    return {'feedback_next_url': request.build_absolute_uri()}
