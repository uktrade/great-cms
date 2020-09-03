from sso import helpers as sso_helpers
from core.models import DetailPage, ListPage, CuratedListPage


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


def get_ancestor(page, ancestor_class):
    # Seek up the tree to fin a page matching class
    while page:
        if isinstance(page.specific, ancestor_class):
            return page
        page = page.get_parent()


def get_read_progress(user, context={}):
    # Gets all detail pages and uses the parental tree to get a list of learning
    # sections with a count of read lessons in each

    def lesson_comparator(lp):
        total = lp.get('total_pages')
        read = lp.get('read_count')
        return total - read if read else -1

    lessons_in_progress = False
    completed = set()
    data = sso_helpers.get_lesson_completed(user.session_id)
    for lesson in data.get('lesson_completed', []):
        completed.add(lesson.get('lesson'))
    page_map = {}
    for detail_page in DetailPage.objects.live():
        list_page = get_ancestor(detail_page, CuratedListPage)
        if list_page:
            page_map[list_page.id] = page_map.get(
                list_page.id) or {'total_pages': 0, 'read_count': 0, 'page': list_page}
            page_map[list_page.id]['total_pages'] += 1
            if detail_page.id in completed:
                page_map[list_page.id]['read_count'] += 1
                lessons_in_progress = True
    list_pages = list(page_map.values())
    list_pages.sort(key=lesson_comparator, reverse=True)
    return {
        'list_pages': list_pages,
        'lessons_in_progress': lessons_in_progress
    }
