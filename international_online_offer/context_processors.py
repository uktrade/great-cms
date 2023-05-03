from international_online_offer.models import get_user_data_from_db_or_session


def user(request):
    user = get_user_data_from_db_or_session(request)
    return {'user': user}
