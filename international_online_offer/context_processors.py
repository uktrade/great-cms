from international_online_offer.models import UserData


def eyb_user(request):
    return (
        {'eyb_user': UserData.objects.filter(hashed_uuid=request.user.hashed_uuid).first()}
        if hasattr(request, 'user')
        and hasattr(request.user, 'is_authenticated')
        and request.user.is_authenticated
        and hasattr(request.user, 'hashed_uuid')
        else {}
    )


def feedback_next_url(request):
    return {'feedback_next_url': request.build_absolute_uri()}
