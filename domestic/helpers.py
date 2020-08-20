from sso import helpers as sso_helpers
from core.models import DetailPage


def check_route(route_type, context, user_profile):
    # Check if this route is valid to show given user context
    if route_type == 'learn':
        total_read = 0
        for list_page in context.get('list_pages'):
            total_read += list_page.get('read_count')
        return total_read == 0

    elif route_type == 'target':
        return not user_profile or not user_profile.expertise_countries_labels
    elif route_type == 'plan':
        # TODO:
        # We should add a check to see if export plan is started in here
        return True


def build_route_context(user, context={}):
    # Find all route compoennts and crate a routes list where blocks are included dependent on state

    routes = []
    page_context = context.get('page')
    user_profile = user.company
    for component in (page_context and page_context.components) or []:
        if component.block_type == 'route':
            if check_route(component.value.get('route_type'), context, user_profile):
                routes.append(component)
    return routes


def get_read_progress(user, context={}):
    # Gets all detail pages and uses the parental tree to get a list of learning
    # sections with a count of read lessons in each

    def lesson_comparator(lp):
        total = lp.get('total_pages')
        read = lp.get('read_count')
        return total - read if read else -1

    completed = set()
    for lesson in sso_helpers.get_lesson_completed(user.session_id).get('lesson_completed') or []:
        completed.add(lesson.get('lesson'))
    list_pages = {}
    for detail_page in DetailPage.objects.live():
        list_page = detail_page.get_parent().get_parent()
        list_pages[list_page.id] = list_pages.get(
            list_page.id) or {'total_pages': 0, 'read_count': 0, 'page': list_page}
        list_pages[list_page.id]['total_pages'] += 1
        if detail_page.id in completed:
            list_pages[list_page.id]['read_count'] += 1
    result = list(list_pages.values())
    result.sort(key=lesson_comparator, reverse=True)
    return result
