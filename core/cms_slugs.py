from django.contrib.sites.shortcuts import get_current_site

# CMS SLUGS slugs that are referenced in the code base. These are considered constants
# If CMS slugs change they should be changed here to prevent 404.

DASHBOARD_URL = '/dashboard/'

LOGIN_URL = '/login/'
SIGNUP_URL = '/signup/'

PRIVACY_NOTICE_URL = '/privacy-notice/'
PRIVACY_POLICY_URL = '/privacy/'
# This special-case page existed in Great V1, so was brought to Great V2 with the same path.
PRIVACY_POLICY_URL__CONTACT_TRIAGE_FORMS_SPECIAL_PAGE = '/privacy/privacy-notice-great-domestic/'
TERMS_URL = '/terms-and-conditions/'

# The following are _not_ actually in the CMS but are TEMPORARILY referencing
# paths on the BAU/V1 infrastrcture, so are as brittle as CMS slugs can be.
# These ones will be removed when the V1->V2 migration is complete
CONTACT_URL = '/contact/'
FEEDBACK_CONTACT_URL = '/contact/feedback/'

DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE = '/support/export-support/'

def get_dashboard_url(request):
    """
    Returns the default dashboard URL depending on site url.

    This function exists purely as technical debt for the transition period
    where both great.gov.uk and the business growth service exist. Depending
    on the root url, it will return one of two default DASHBOARD_URL paths.
    """

    domain = get_current_site(request).domain

    if any(word in domain for word in ['bgs', 'business']):
        return '/export-from-uk/dashboard/'
    else:
        return '/dashboard/'



