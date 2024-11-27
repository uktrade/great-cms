from django import template

register = template.Library()


@register.inclusion_tag('_cta_banner.html')
def render_course_cta():
    return {
        'headingText': 'Unlock your export potential',
        'leadingText': (
            'Join the UK Export Academy for instant access to live events '
            'with Q&A, and event recordings available on demand.'
        ),
        'backgroundClass': 'great-ds-cta-banner--bg-green',
        'actionLinkClass': 'great-ds-action-link--black',
        'signInLink': {'href': '/login', 'preLinkText': 'Already joined the UK Export Academy?', 'linkText': 'Sign in'},
        'signUpLink': {'href': '/signup', 'linkText': 'Sign up to get started'},
        'landscapeImagePath': '/static/images/ukea-cta-image.png',
    }
