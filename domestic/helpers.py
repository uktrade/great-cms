from collections import defaultdict
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
    # Seek up the tree to find a page matching class
    return ancestor_class.objects.live().ancestor_of(page).specific().first()


def module_has_lesson_configured_in_topic(
    module_page: CuratedListPage,
    lesson_page: DetailPage
) -> bool:
    lesson_topic_page = lesson_page.get_parent().specific
    for topic_page in module_page.get_topics().live():
        if topic_page == lesson_topic_page:
            return True
    return False


def get_lesson_completion_status(user, context={}):
    """Gets all lesson pages (DetailPages) and uses the parental tree to get a list
    of modules (CuratedListPages), with some grouping of DetailPages by their parent
    TopicPage (which itself is a child of CuratedListPage)

    Example output:
    {
        'lessons_in_progress': True,
        'module_pages': [
            {
                'total_pages': 7,
                'completion_count': 4,
                'page': <CuratedListPage: Identify opportunities>,
                'completed_lesson_pages': defaultdict(
                    <class 'set'>, {
                    'b7eca1bf-8b43-4737-91e4-913dfeb2c5d8': {10, 26},
                    '044e1343-f2ce-4089-8ce9-17093b9d36b8': {18, 20}}
                )
            },
            ...
        ]
    }"""

    def lesson_comparator(lp):
        total = lp.get('total_pages')
        read = lp.get('completion_count')
        return total - read if read else -1

    lessons_in_progress = False
    completed = set()
    data = sso_helpers.get_lesson_completed(user.session_id)
    for lesson in data.get('lesson_completed', []):
        completed.add(lesson.get('lesson'))

    page_map = {}

    # TODO: refactor further to simplify
    for detail_page in DetailPage.objects.live():
        module_page = get_ancestor(detail_page, CuratedListPage)
        if module_page:
            page_map[module_page.id] = (
                page_map.get(module_page.id) or {
                    'total_pages': 0,
                    'completion_count': 0,
                    'page': module_page,
                    'completed_lesson_pages': defaultdict(set)
                }
            )

            # Only proceeed with `detail_page` if it is CURRENTLY
            # configured in a topic for this module
            if not module_has_lesson_configured_in_topic(
                module_page=module_page.specific,
                lesson_page=detail_page.specific
            ):
                continue

            page_map[module_page.id]['total_pages'] += 1

            if detail_page.id in completed:
                topic_id_as_key = detail_page.get_parent().id
                page_map[module_page.id]['completed_lesson_pages'][topic_id_as_key].add(
                    detail_page.id
                )
                page_map[module_page.id]['completion_count'] += 1
                # Take care: this next var means 'lessons have been attempted',
                # not 'lessons are _currently_ in progress', because it doesn't
                # allow for someone having completed them all
                lessons_in_progress = True

    module_pages = list(page_map.values())
    module_pages.sort(key=lesson_comparator, reverse=True)
    return {
        'module_pages': module_pages,
        'lessons_in_progress': lessons_in_progress
    }
