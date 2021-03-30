from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.views.generic import RedirectView

import sso_profile.business_profile.views
import sso_profile.core.views
import sso_profile.enrolment.views
import sso_profile.exops.views
import sso_profile.personal_profile.views
import sso_profile.soo.views

app_name = 'sso_profile'


def company_required(function):
    inner = user_passes_test(lambda user: bool(user.company), reverse_lazy('business-profile'), None)
    return login_required(inner(function))


def no_company_required(function):
    url = reverse_lazy('business-profile')
    inner = user_passes_test(lambda user: not bool(getattr(user, 'company', None)), url, None)
    return inner(function)


def company_admin_required(function):
    inner = user_passes_test(lambda user: user.is_company_admin, reverse_lazy('business-profile'), None)
    return login_required(inner(function))


api_urls = [
    url(
        r'^v1/companies-house-search/$',
        sso_profile.core.views.CompaniesHouseSearchAPIView.as_view(),
        name='companies-house-search',
    ),
    url(r'^v1/postcode-search/$', sso_profile.core.views.AddressSearchAPIView.as_view(), name='postcode-search'),
]

urls_personal_profile = [
    url(r'^$', login_required(sso_profile.personal_profile.views.PersonalProfileView.as_view()), name='display'),
    url(
        r'^edit/$',
        login_required(sso_profile.personal_profile.views.PersonalProfileEditFormView.as_view()),
        name='edit',
    ),
]

urlpatterns = [
    url(r'^api/', include((api_urls, 'api'), namespace='api')),
    url(r'^about/$', sso_profile.core.views.AboutView.as_view(), name='about'),
    url(
        r'^selling-online-overseas/$',
        login_required(sso_profile.soo.views.SellingOnlineOverseasView.as_view()),
        name='selling-online-overseas',
    ),
    url(
        r'^export-opportunities/applications/$',
        login_required(sso_profile.exops.views.ExportOpportunitiesApplicationsView.as_view()),
        name='export-opportunities-applications',
    ),
    url(
        r'^export-opportunities/email-alerts/$',
        login_required(sso_profile.exops.views.ExportOpportunitiesEmailAlertsView.as_view()),
        name='export-opportunities-email-alerts',
    ),
    url(r'^enrol/$', sso_profile.enrolment.views.EnrolmentStartView.as_view(), name='enrolment-start'),
    url(
        r'^enrol/business-type/$',
        sso_profile.enrolment.views.BusinessTypeRoutingView.as_view(),
        name='enrolment-business-type',
    ),
    url(
        r'^enrol/business-type/companies-house/(?P<step>.+)/$',
        sso_profile.enrolment.views.CompaniesHouseEnrolmentView.as_view(
            url_name='enrolment-companies-house', done_step_name='finished'
        ),
        name='enrolment-companies-house',
    ),
    url(
        r'^enrol/business-type/non-companies-house-company/(?P<step>.+)/$',
        sso_profile.enrolment.views.NonCompaniesHouseEnrolmentView.as_view(
            url_name='enrolment-sole-trader', done_step_name='finished'
        ),
        name='enrolment-sole-trader',
    ),
    url(
        r'^enrol/business-type/individual/start/$',
        sso_profile.enrolment.views.IndividualUserEnrolmentInterstitialView.as_view(),
        name='enrolment-individual-interstitial',
    ),
    url(
        r'^enrol/business-type/individual/(?P<step>.+)/$',
        sso_profile.enrolment.views.IndividualUserEnrolmentView.as_view(
            url_name='enrolment-individual', done_step_name='finished'
        ),
        name='enrolment-individual',
    ),
    url(
        r'^enrol/business-type/overseas-business/$',
        sso_profile.enrolment.views.EnrolmentOverseasBusinessView.as_view(),
        name='enrolment-overseas-business',
    ),
    url(
        r'^enrol/pre-verified/(?P<step>.+)/$',
        sso_profile.enrolment.views.PreVerifiedEnrolmentView.as_view(
            url_name='enrolment-pre-verified', done_step_name='finished'
        ),
        name='enrolment-pre-verified',
    ),
    url(
        r'^enrol/pre-verified/$',
        RedirectView.as_view(
            url=reverse_lazy('enrolment-pre-verified', kwargs={'step': 'user-account'}), query_string=True
        ),
    ),
    url(
        r'^enrol/collaborate/(?P<step>.+)/$',
        no_company_required(
            sso_profile.enrolment.views.CollaboratorEnrolmentView.as_view(
                url_name='enrolment-collaboration', done_step_name='finished'
            )
        ),
        name='enrolment-collaboration',
    ),
    url(
        r'^enrol/resend-verification/(?P<step>.+)/$',
        sso_profile.enrolment.views.ResendVerificationCodeView.as_view(
            url_name='resend-verification', done_step_name='finished'
        ),
        name='resend-verification',
    ),
    url(
        r'^business-profile/$',
        sso_profile.business_profile.views.BusinessProfileView.as_view(),
        name='business-profile',
    ),
    url(
        r'^business-profile/admin/$',
        company_admin_required(sso_profile.business_profile.views.AdminCollaboratorsListView.as_view()),
        name='business-profile-admin-tools',
    ),
    url(
        r'^business-profile/disconnect/$',
        company_required(sso_profile.business_profile.views.MemberDisconnectFromCompany.as_view()),
        name='disconnect-account',
    ),
    url(
        r'^business-profile/admin/collaborator/(?P<sso_id>[0-9]+)/$',
        company_admin_required(sso_profile.business_profile.views.AdminCollaboratorEditFormView.as_view()),
        name='business-profile-admin-collaborator-edit',
    ),
    url(
        r'^business-profile/admin/disconnect/$',
        company_admin_required(sso_profile.business_profile.views.AdminDisconnectFormView.as_view()),
        name='business-profile-admin-disconnect',
    ),
    url(
        r'^business-profile/admin/transfer/$',
        company_admin_required(sso_profile.business_profile.views.AdminInviteNewAdminFormView.as_view()),
        name='business-profile-admin-invite-administrator',
    ),
    url(
        r'^business-profile/admin/invite/$',
        company_admin_required(sso_profile.business_profile.views.AdminInviteCollaboratorFormView.as_view()),
        name='business-profile-admin-invite-collaborator',
    ),
    url(
        r'^business-profile/admin/invite/delete/$',
        company_admin_required(sso_profile.business_profile.views.AdminInviteCollaboratorDeleteFormView.as_view()),
        name='business-profile-collaboration-invite-delete',
    ),
    url(
        r'^business-profile/social-links/$',
        company_required(sso_profile.business_profile.views.SocialLinksFormView.as_view()),
        name='business-profile-social',
    ),
    url(
        r'^business-profile/email/$',
        company_required(sso_profile.business_profile.views.EmailAddressFormView.as_view()),
        name='business-profile-email',
    ),
    url(
        r'^business-profile/description/$',
        company_required(sso_profile.business_profile.views.DescriptionFormView.as_view()),
        name='business-profile-description',
    ),
    url(
        r'^business-profile/website/$',
        company_required(sso_profile.business_profile.views.WebsiteFormView.as_view()),
        name='business-profile-website',
    ),
    url(
        r'^business-profile/logo/$',
        company_required(sso_profile.business_profile.views.LogoFormView.as_view()),
        name='business-profile-logo',
    ),
    url(
        r'^business-profile/personal-details/$',
        login_required(sso_profile.business_profile.views.PersonalDetailsFormView.as_view()),
        name='business-profile-personal-details',
    ),
    url(
        r'^business-profile/publish/$',
        company_required(sso_profile.business_profile.views.PublishFormView.as_view()),
        name='business-profile-publish',
    ),
    url(
        r'^business-profile/business-details/$',
        company_required(sso_profile.business_profile.views.BusinessDetailsFormView.as_view()),
        name='business-profile-business-details',
    ),
    url(
        r'^business-profile/case-study/(?P<id>[0-9]+)/(?P<step>.+)/$',
        company_required(
            sso_profile.business_profile.views.CaseStudyWizardEditView.as_view(
                url_name='business-profile-case-study-edit'
            )
        ),
        name='business-profile-case-study-edit',
    ),
    url(
        r'^business-profile/case-study/(?P<step>.+)/$',
        company_required(
            sso_profile.business_profile.views.CaseStudyWizardCreateView.as_view(url_name='business-profile-case-study')
        ),
        name='business-profile-case-study',
    ),
    url(
        r'^business-profile/add-expertise/$',
        company_required(sso_profile.business_profile.views.ExpertiseRoutingFormView.as_view()),
        name='business-profile-expertise-routing',
    ),
    url(
        r'^business-profile/add-expertise/regions/$',
        company_required(sso_profile.business_profile.views.RegionalExpertiseFormView.as_view()),
        name='business-profile-expertise-regional',
    ),
    url(
        r'^business-profile/add-expertise/countries/$',
        company_required(sso_profile.business_profile.views.CountryExpertiseFormView.as_view()),
        name='business-profile-expertise-countries',
    ),
    url(
        r'^business-profile/add-expertise/industries/$',
        company_required(sso_profile.business_profile.views.IndustryExpertiseFormView.as_view()),
        name='business-profile-expertise-industries',
    ),
    url(
        r'^business-profile/add-expertise/languages/$',
        company_required(sso_profile.business_profile.views.LanguageExpertiseFormView.as_view()),
        name='business-profile-expertise-languages',
    ),
    url(
        r'^business-profile/products-and-services/$',
        RedirectView.as_view(pattern_name='business-profile-expertise-products-services-routing'),
        name='business-profile-products-and-services',
    ),
    url(
        r'^business-profile/add-expertise/products-and-services/$',
        company_required(sso_profile.business_profile.views.ProductsServicesRoutingFormView.as_view()),
        name='business-profile-expertise-products-services-routing',
    ),
    url(
        r'^business-profile/add-expertise/products-and-services/other/$',
        company_required(sso_profile.business_profile.views.ProductsServicesOtherFormView.as_view()),
        name='business-profile-expertise-products-services-other',
    ),
    url(
        r'^business-profile/add-expertise/products-and-services/(?P<category>.+)/$',
        company_required(sso_profile.business_profile.views.ProductsServicesFormView.as_view()),
        name='business-profile-expertise-products-services',
    ),
    url(
        r'^business-profile/verify/request/$',
        company_required(sso_profile.business_profile.views.IdentityVerificationRequestFormView.as_view()),
        name='business-profile-request-to-verify',
    ),
    url(r'^personal-profile/', include((urls_personal_profile, 'personal-profile'), namespace='personal-profile')),
]
