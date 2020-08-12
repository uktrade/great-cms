
def check_route(route_type, context, user_profile):
    # Check if this route is valid to show given user context
    if route_type == 'learn':
        total_read = 0
        for list_page in context.get('list_pages'):
            total_read += list_page.read_count
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
