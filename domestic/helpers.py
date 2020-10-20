from sso import helpers as sso_helpers
from core.models import DetailPage, CuratedListPage


def build_route_context(user, context={}):
    # Find all route components and create a routes list
    routes = {}
    page_context = context.get('page')
    for component in (page_context and page_context.components) or []:
        if component.block_type == 'route':
            route_type = component.value.get('route_type')
            routes[component.value.get('route_type')] = component
            if route_type == 'target':
                export_plan = context.get('export_plan') or {}
                component.value['enabled'] = not len(export_plan.get('export_countries', []))
            if route_type == 'learn':
                component.value['enabled'] = not context.get('lessons_in_progress')
            if route_type == 'plan':
                component.value['enabled'] = not context.get('export_plan_in_progress')

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
        module_page = get_ancestor(detail_page, CuratedListPage)
        if module_page:
            page_map[module_page.id] = page_map.get(
                module_page.id) or {'total_pages': 0, 'read_count': 0, 'page': module_page}
            page_map[module_page.id]['total_pages'] += 1
            if detail_page.id in completed:
                page_map[module_page.id]['read_count'] += 1
                lessons_in_progress = True
    module_pages = list(page_map.values())
    module_pages.sort(key=lesson_comparator, reverse=True)
    return {
        'module_pages': module_pages,
        'lessons_in_progress': lessons_in_progress
    }
