def is_using_triage(request):
    current_url = request.build_absolute_uri(request.path)
    # sector_url = str(reverse_lazy('international_online_offer:sector'))
    # TODO update this to do transactional nav for captial investor triage
    sector_url = 'http://google.com'
    triage_urls = [sector_url]
    for url in triage_urls:
        if url in current_url:
            return True
    return False


def hide_primary_nav(request):
    hide_primary_nav = is_using_triage(request)
    return {'hide_primary_nav': hide_primary_nav}
