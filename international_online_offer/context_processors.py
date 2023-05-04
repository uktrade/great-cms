from international_online_offer.models import get_user_data_from_db_or_session


def eyb_user(request):
    eyb_user = get_user_data_from_db_or_session(request)
    return {'eyb_user': eyb_user}
