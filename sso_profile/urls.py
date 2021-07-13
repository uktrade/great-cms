from django.conf.urls import include
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

import sso_profile.business_profile.views
import sso_profile.common.views
import sso_profile.enrolment.views
import sso_profile.exops.views
import sso_profile.personal_profile.views
import sso_profile.soo.views
from directory_constants import urls

app_name = 'sso_profile'
SIGNUP_URL = reverse_lazy('core:signup')


def no_company_required(function):
    _url = reverse_lazy('sso_profile:business-profile')
    inner = user_passes_test(
        lambda user: not bool(getattr(user, 'company', None)),
        _url,
        None,
    )
    return inner(function)


def company_required(function):
    inner = user_passes_test(
        lambda user: bool(user.company),
        reverse_lazy('sso_profile:business-profile'),
        None,
    )
    return login_required(
        inner(function),
        login_url=SIGNUP_URL,
    )


def company_admin_required(function):
    inner = user_passes_test(
        lambda user: user.is_company_admin,
        reverse_lazy('sso_profile:business-profile'),
        None,
    )
    return login_required(
        inner(function),
        login_url=SIGNUP_URL,
    )


api_urls = [
    path(
        'v1/companies-house-search/',
        sso_profile.common.views.CompaniesHouseSearchAPIView.as_view(),
        name='companies-house-search',
    ),
    path(
        'v1/postcode-search/',
        sso_profile.common.views.AddressSearchAPIView.as_view(),
        name='postcode-search',
    ),
]


urls_personal_profile = [
    # included later on, beneath a namespacing path
    path(
        '',
        login_required(
            sso_profile.personal_profile.views.PersonalProfileView.as_view(),
            login_url=SIGNUP_URL,
        ),
        name='display',
    ),
    path(
        'edit/',
        login_required(
            sso_profile.personal_profile.views.PersonalProfileEditFormView.as_view(),
            login_url=SIGNUP_URL,
        ),
        name='edit',
    ),
]


urlpatterns = [
    path(
        '',
        sso_profile.common.views.LandingPageView.as_view(),
        name='index',
    ),
    path(
        'about/',
        sso_profile.common.views.AboutView.as_view(),
        name='about',
    ),
    path(
        'api/',
        include((api_urls, 'api'), namespace='sso_profile_api'),
    ),
    path(
        'selling-online-overseas/',
        login_required(sso_profile.soo.views.SellingOnlineOverseasView.as_view()),
        name='selling-online-overseas',
    ),
    path(
        'export-opportunities/applications/',
        login_required(
            sso_profile.exops.views.ExportOpportunitiesApplicationsView.as_view(),
            login_url=SIGNUP_URL,
        ),
        name='export-opportunities-applications',
    ),
    path(
        'export-opportunities/email-alerts/',
        login_required(
            sso_profile.exops.views.ExportOpportunitiesEmailAlertsView.as_view(),
            login_url=SIGNUP_URL,
        ),
        name='export-opportunities-email-alerts',
    ),
    path(
        'enrol/',
        sso_profile.enrolment.views.EnrolmentStartView.as_view(),
        name='enrolment-start',
    ),
    path(
        'enrol/business-type/',
        sso_profile.enrolment.views.BusinessTypeRoutingView.as_view(),
        name='enrolment-business-type',
    ),
    path(
        'enrol/business-type/companies-house/<str:step>/',
        sso_profile.enrolment.views.CompaniesHouseEnrolmentView.as_view(
            url_name='sso_profile:enrolment-companies-house',
            done_step_name='finished',
        ),
        name='enrolment-companies-house',
    ),
    path(
        'enrol/business-type/non-companies-house-company/<str:step>/',
        sso_profile.enrolment.views.NonCompaniesHouseEnrolmentView.as_view(
            url_name='sso_profile:enrolment-sole-trader',
            done_step_name='finished',
        ),
        name='enrolment-sole-trader',
    ),
    path(
        'enrol/business-type/individual/start/',
        sso_profile.enrolment.views.IndividualUserEnrolmentInterstitialView.as_view(),
        name='enrolment-individual-interstitial',
    ),
    path(
        'enrol/business-type/individual/<str:step>/',
        sso_profile.enrolment.views.IndividualUserEnrolmentView.as_view(
            url_name='sso_profile:enrolment-individual',
            done_step_name='finished',
        ),
        name='enrolment-individual',
    ),
    path(
        'enrol/business-type/overseas-business/',
        sso_profile.enrolment.views.EnrolmentOverseasBusinessView.as_view(),
        name='enrolment-overseas-business',
    ),
    path(
        'enrol/pre-verified/<str:step>/',
        sso_profile.enrolment.views.PreVerifiedEnrolmentView.as_view(
            url_name='sso_profile:enrolment-pre-verified',
            done_step_name='finished',
        ),
        name='enrolment-pre-verified',
    ),
    path(
        'enrol/pre-verified/',
        RedirectView.as_view(
            url=reverse_lazy(
                'sso_profile:enrolment-pre-verified',
                kwargs={'step': 'user-account'},
            ),
            query_string=True,
        ),
    ),
    path(
        'enrol/collaborate/<str:step>/',
        no_company_required(
            sso_profile.enrolment.views.CollaboratorEnrolmentView.as_view(
                url_name='sso_profile:enrolment-collaboration',
                done_step_name='finished',
            )
        ),
        name='enrolment-collaboration',
    ),
    path(
        'enrol/resend-verification/<str:step>/',
        sso_profile.enrolment.views.ResendVerificationCodeView.as_view(
            url_name='sso_profile:resend-verification',
            done_step_name='finished',
        ),
        name='resend-verification',
    ),
    path(
        'business-profile/',
        login_required(
            sso_profile.business_profile.views.BusinessProfileView.as_view(),
            login_url=reverse_lazy('sso_profile:enrolment-start'),
        ),
        name='business-profile',
    ),
    path(
        'business-profile/admin/',
        company_admin_required(sso_profile.business_profile.views.AdminCollaboratorsListView.as_view()),
        name='business-profile-admin-tools',
    ),
    path(
        'business-profile/disconnect/',
        company_required(sso_profile.business_profile.views.MemberDisconnectFromCompany.as_view()),
        name='disconnect-account',
    ),
    path(
        'business-profile/admin/collaborator/<int:sso_id>/',
        company_admin_required(sso_profile.business_profile.views.AdminCollaboratorEditFormView.as_view()),
        name='business-profile-admin-collaborator-edit',
    ),
    path(
        'business-profile/admin/disconnect/',
        company_admin_required(sso_profile.business_profile.views.AdminDisconnectFormView.as_view()),
        name='business-profile-admin-disconnect',
    ),
    path(
        'business-profile/admin/transfer/',
        company_admin_required(sso_profile.business_profile.views.AdminInviteNewAdminFormView.as_view()),
        name='business-profile-admin-invite-administrator',
    ),
    path(
        'business-profile/admin/invite/',
        company_admin_required(sso_profile.business_profile.views.AdminInviteCollaboratorFormView.as_view()),
        name='business-profile-admin-invite-collaborator',
    ),
    path(
        'business-profile/admin/invite/delete/',
        company_admin_required(sso_profile.business_profile.views.AdminInviteCollaboratorDeleteFormView.as_view()),
        name='business-profile-collaboration-invite-delete',
    ),
    path(
        'business-profile/social-links/',
        company_required(sso_profile.business_profile.views.SocialLinksFormView.as_view()),
        name='business-profile-social',
    ),
    path(
        'business-profile/email/',
        company_required(sso_profile.business_profile.views.EmailAddressFormView.as_view()),
        name='business-profile-email',
    ),
    path(
        'business-profile/description/',
        company_required(sso_profile.business_profile.views.DescriptionFormView.as_view()),
        name='business-profile-description',
    ),
    path(
        'business-profile/website/',
        company_required(sso_profile.business_profile.views.WebsiteFormView.as_view()),
        name='business-profile-website',
    ),
    path(
        'business-profile/logo/',
        company_required(sso_profile.business_profile.views.LogoFormView.as_view()),
        name='business-profile-logo',
    ),
    path(
        'business-profile/personal-details/',
        login_required(
            sso_profile.business_profile.views.PersonalDetailsFormView.as_view(),
            login_url=SIGNUP_URL,
        ),
        name='business-profile-personal-details',
    ),
    path(
        'business-profile/publish/',
        company_required(
            sso_profile.business_profile.views.PublishFormView.as_view(),
        ),
        name='business-profile-publish',
    ),
    path(
        'business-profile/business-details/',
        company_required(
            sso_profile.business_profile.views.BusinessDetailsFormView.as_view(),
        ),
        name='business-profile-business-details',
    ),
    path(
        'business-profile/case-study/<int:id>/<str:step>/',
        company_required(
            sso_profile.business_profile.views.CaseStudyWizardEditView.as_view(
                url_name='sso_profile:business-profile-case-study-edit'
            )
        ),
        name='business-profile-case-study-edit',
    ),
    path(
        'business-profile/case-study/<str:step>/',
        company_required(
            sso_profile.business_profile.views.CaseStudyWizardCreateView.as_view(
                url_name='sso_profile:business-profile-case-study'
            ),
        ),
        name='business-profile-case-study',
    ),
    path(
        'business-profile/add-expertise/',
        company_required(
            sso_profile.business_profile.views.ExpertiseRoutingFormView.as_view(),
        ),
        name='business-profile-expertise-routing',
    ),
    path(
        'business-profile/add-expertise/regions/',
        company_required(
            sso_profile.business_profile.views.RegionalExpertiseFormView.as_view(),
        ),
        name='business-profile-expertise-regional',
    ),
    path(
        'business-profile/add-expertise/countries/',
        company_required(
            sso_profile.business_profile.views.CountryExpertiseFormView.as_view(),
        ),
        name='business-profile-expertise-countries',
    ),
    path(
        'business-profile/add-expertise/industries/',
        company_required(
            sso_profile.business_profile.views.IndustryExpertiseFormView.as_view(),
        ),
        name='business-profile-expertise-industries',
    ),
    path(
        'business-profile/add-expertise/languages/',
        company_required(
            sso_profile.business_profile.views.LanguageExpertiseFormView.as_view(),
        ),
        name='business-profile-expertise-languages',
    ),
    path(
        'business-profile/products-and-services/',
        RedirectView.as_view(
            pattern_name='business-profile-expertise-products-services-routing',
        ),
        name='business-profile-products-and-services',
    ),
    path(
        'business-profile/add-expertise/products-and-services/',
        company_required(
            sso_profile.business_profile.views.ProductsServicesRoutingFormView.as_view(),
        ),
        name='business-profile-expertise-products-services-routing',
    ),
    path(
        'business-profile/add-expertise/products-and-services/other/',
        company_required(
            sso_profile.business_profile.views.ProductsServicesOtherFormView.as_view(),
        ),
        name='business-profile-expertise-products-services-other',
    ),
    path(
        'business-profile/add-expertise/products-and-services/<str:category>/',
        company_required(
            sso_profile.business_profile.views.ProductsServicesFormView.as_view(),
        ),
        name='business-profile-expertise-products-services',
    ),
    path(
        'business-profile/verify/request/',
        company_required(
            sso_profile.business_profile.views.IdentityVerificationRequestFormView.as_view(),
        ),
        name='business-profile-request-to-verify',
    ),
    path(
        'personal-profile/',
        include((urls_personal_profile, 'personal-profile'), namespace='personal-profile'),
    ),
    path(
        'find-a-buyer/<slug:path>/',
        RedirectView.as_view(
            url=urls.domestic.SINGLE_SIGN_ON_PROFILE / 'business-profile/%(path)s',
            query_string=True,
        ),
    ),
    path(
        'find-a-buyer/',
        RedirectView.as_view(
            url=urls.domestic.SINGLE_SIGN_ON_PROFILE / 'business-profile/',
            query_string=True,
        ),
    ),
]
