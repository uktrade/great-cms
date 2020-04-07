from collections import namedtuple
from enum import Enum

from selenium.webdriver.common.by import By


class SelectorsEnum(Enum):

    @property
    def by(self):
        return self.value.by

    @property
    def selector(self):
        return self.value.selector

    @property
    def type(self):
        return self.value.type

    @property
    def is_visible(self):
        return self.value.is_visible

    @property
    def is_authenticated(self):
        return self.value.is_authenticated


class ElementType(Enum):
    BUTTON = 'button'
    CHECKBOX = 'checkbox'
    HEADER = 'header'
    IFRAME = 'iframe'
    IMAGE = 'img'
    INPUT = 'input'
    LABEL = 'label'
    LINK = 'a'
    RADIO = 'radio'
    SELECT = 'select'
    SPAN = 'span'
    SUBMIT = 'submit'
    TEXTAREA = 'textarea'
    UL = 'ul'

    def __str__(self):
        return self.value


Selector = namedtuple(
    'Selector',
    [
        'by',
        'selector',
        'type',
        'is_visible',
        'is_authenticated',
    ],
)
# define default values for Selector named tuple
Selector.__new__.__defaults__ = (None, None, None, True, False)


class HeaderCommon(SelectorsEnum):
    HEADER_SECTION = Selector(By.ID, 'header', ElementType.HEADER)
    LOGO_LINK = Selector(By.ID, 'header-logo-link', ElementType.LINK)
    LOGO = Selector(By.ID, 'header-logo-exporting-is-great', ElementType.IMAGE)
    SERVICES_AREA = Selector(By.ID, 'services-area', ElementType.UL)
    LEARNING = Selector(By.ID, 'header-link-learning', ElementType.LINK)
    EXPORTING_PLAN = Selector(By.ID, 'header-link-exporting-plan', ElementType.LINK)
    MARKETS = Selector(By.ID, 'header-link-markets', ElementType.LINK)
    SERVICES = Selector(By.ID, 'header-link-services', ElementType.LINK)
    USER_STATE_AREA = Selector(By.ID, 'user-state-area', ElementType.UL)


class HeaderSignUp(SelectorsEnum):
    SIGN_UP = Selector(By.ID, 'header-sign-in-link', ElementType.LINK)


class HeaderSignedIn(SelectorsEnum):
    NOTIFICATIONS = Selector(By.ID, 'header-link-notifications', ElementType.LINK)
    USER_PROFILE = Selector(By.ID, 'header-link-user-profile', ElementType.LINK)
    USER_PROFILE_EMAIL = Selector(By.ID, 'header-link-user-profile-email-link', ElementType.LINK)
    DASHBOARD = Selector(By.ID, 'header-link-dashboard', ElementType.LINK)


class DashboardContents(SelectorsEnum):
    HERO = Selector(By.ID, 'great-hero')
    WELCOME = Selector(By.ID, 'great-hero-welcome')
    YOUR_PROGRESS_CARD = Selector(By.ID, 'your-progress-card')
    EXPORT_PLAN_CARD = Selector(By.ID, 'your-export-plan-card')
    DID_YOU_KNOW_CARD = Selector(By.ID, 'did-you-know-card')
    DISCOVER_NEW_MARKETS_CARD = Selector(By.ID, 'discover-new-markets-card')
    EXPORT_OPPORTUNITIES_CARD = Selector(By.ID, 'export-opportunities-card')
    EVENTS_CARD = Selector(By.ID, 'events-card')
    TARIFFS_AND_DUTIES_CARD = Selector(By.ID, 'tariffs-and-duties-card')


class DashboardContentsWithoutSuccess(SelectorsEnum):
    LEARNING_BOX = Selector(By.ID, 'great-continue-learning-box')


class DashboardContentsOnSuccess(SelectorsEnum):
    SUCCESS_CARD = Selector(By.ID, 'great-mvp-success-card')


class DashboardReadingProgress(SelectorsEnum):
    YOUR_PROGRESS_CARD = Selector(By.ID, 'your-progress-card')
    TOPICS_HEADERS = Selector(By.CSS_SELECTOR, 'h3[id^=topics-]')
    TOPICS_READ_PROGRESS = Selector(By.CSS_SELECTOR, 'div[id^=topics-read-progress-]')


class SignUpModal(SelectorsEnum):
    MODAL = Selector(By.ID, 'signup-modal')
    LINKEDIN = Selector(By.ID, 'signup-modal-linkedin')
    GOOGLE = Selector(By.ID, 'signup-modal-google')
    LOG_IN = Selector(By.ID, 'signup-modal-log-in')
    T_AND_C = Selector(By.ID, 'signup-modal-t-and-c')
    SUBMIT = Selector(By.ID, 'signup-modal-submit', ElementType.BUTTON)
    EMAIL = Selector(By.ID, 'id_email', ElementType.INPUT)
    PASSWORD = Selector(By.ID, 'id_password', ElementType.INPUT)
    ERROR_MESSAGES = Selector(By.CSS_SELECTOR, 'li.error-message', is_visible=False)


class SignUpModalVerificationCode(SelectorsEnum):
    VERIFICATION_CODE = Selector(By.ID, 'id_code')
    SUBMIT_CODE = Selector(By.ID, 'signup-modal-submit-code', ElementType.BUTTON)


class SignUpModalSuccess(SelectorsEnum):
    MODAL = Selector(By.ID, 'signup-modal-success')
    SUBMIT = Selector(By.ID, 'signup-modal-submit-success', ElementType.BUTTON)


class DashboardModalLetsGetToKnowYou(SelectorsEnum):
    MODAL = Selector(By.ID, 'dashboard-question-modal-lets-get-to-know-you')
    INDUSTRIES_INPUT = Selector(By.ID, 'react-select-2-input', ElementType.INPUT)
    SUBMIT = Selector(By.ID, 'dashboard-question-modal-submit', ElementType.BUTTON)
    ERROR_MESSAGES = Selector(By.CSS_SELECTOR, 'li.error-message', is_visible=False)


class MarketsContainer(SelectorsEnum):
    BREADCRUMBS = Selector(By.ID, 'great-hero')
    BREADCRUMBS_HOME = Selector(By.ID, 'breadcrumbs-home', ElementType.LINK)
    BREADCRUMBS_MARKETS = Selector(By.CSS_SELECTOR, '#great-hero nav li span')
    CONTENT_CONTAINER = Selector(By.ID, 'markets-container')
    FORM = Selector(By.ID, 'markets-form')


class StickyHeader(SelectorsEnum):
    STICKY_HEADER = Selector(By.ID, 'exportplan-country-sector-customisation-bar')
    WHAT = Selector(By.ID, 'exportplan-country-sector-what')
    WHERE = Selector(By.ID, 'exportplan-country-sector-where')
    SHARE = Selector(By.ID, 'exportplan-collaboraton-menu-share', ElementType.LINK)
    DOWNLOAD = Selector(By.ID, 'exportplan-collaboraton-menu-download', ElementType.LINK)


class ExportPlanDashboard(SelectorsEnum):
    ABOUT_YOUR_BUSINESS = Selector(By.ID, 'about-your-business', ElementType.LINK)
    OBJECTIVES = Selector(By.ID, 'objectives', ElementType.LINK)
    TARGET_MARKETS = Selector(By.ID, 'target-markets', ElementType.LINK)
    ADAPTATION = Selector(By.ID, 'adaptation-for-international-markets', ElementType.LINK)
    MARKETING_APPROACH = Selector(By.ID, 'marketing-approach', ElementType.LINK)
    FINANCE = Selector(By.ID, 'finance', ElementType.LINK)
    COSTS_AND_PRICING = Selector(By.ID, 'costs-and-pricing', ElementType.LINK)
    PAYMENT_METHODS = Selector(By.ID, 'payment-methods', ElementType.LINK)
    TRAVEL_AND_BUSINESS_POLICIES = Selector(By.ID, 'travel-and-business-policies', ElementType.LINK)
    BUSINESS_RISK = Selector(By.ID, 'business-risk', ElementType.LINK)
    ACTION_PLAN = Selector(By.ID, 'action-plan', ElementType.LINK)


class ExportPlanDashboardPageTourStep0(SelectorsEnum):
    MODAL = Selector(By.ID, 'page-tour-modal-step-1')
    NEXT = Selector(By.ID, 'page-tour-submit', ElementType.LINK)
    SKIP = Selector(By.ID, 'page-tour-skip', ElementType.LINK)
    HIGHLIGHTED_ELEMENT = None


class ExportPlanDashboardPageTourStep1(SelectorsEnum):
    STEP = Selector(By.ID, 'page-tour-step-where-do-you-want-to-export')
    HIGHLIGHTED_ELEMENT = Selector(By.ID, 'exportplan-country-sector-customisation-bar')
    NEXT = Selector(By.ID, 'page-tour-next-step')


class ExportPlanDashboardPageTourStep2(SelectorsEnum):
    STEP = Selector(By.ID, 'page-tour-step-track-your-progress')
    HIGHLIGHTED_ELEMENT = Selector(By.ID, 'exportplan-completion-progress-indicator')
    NEXT = Selector(By.ID, 'page-tour-next-step')


class ExportPlanDashboardPageTourStep3(SelectorsEnum):
    STEP = Selector(By.ID, 'page-tour-step-learn-as-you-go')
    HIGHLIGHTED_ELEMENT = Selector(By.ID, 'exportplan-continue-leaning-title')
    NEXT = Selector(By.ID, 'page-tour-next-step')


class ExportPlanDashboardPageTourStep4(SelectorsEnum):
    STEP = Selector(By.ID, 'page-tour-step-collaborate-with-your-team-and-international-trade-advisers')
    HIGHLIGHTED_ELEMENT = Selector(By.ID, 'exportplan-collaboraton-menu')
    NEXT = Selector(By.ID, 'page-tour-next-step')


class ExportPlanDashboardPageTourStep5(SelectorsEnum):
    STEP = Selector(By.ID, 'page-tour-step-lets-start')
    HIGHLIGHTED_ELEMENT = Selector(By.ID, 'about-your-business')
    NEXT = Selector(By.ID, 'page-tour-start-now', ElementType.LINK)


class ExportPlanTargetMarkets(SelectorsEnum):
    SIDEBAR = Selector(By.ID, 'sidebar-content')
    ABOUT_YOUR_BUSINESS = Selector(By.ID, 'sidebar-about-your-business', ElementType.LINK)
    OBJECTIVES = Selector(By.ID, 'sidebar-objectives', ElementType.LINK)
    TARGET_MARKETS = Selector(By.ID, 'sidebar-target-markets', ElementType.LINK)
    ADAPTATION = Selector(By.ID, 'sidebar-adaptation-for-international-markets', ElementType.LINK)
    MARKETING_APPROACH = Selector(By.ID, 'sidebar-marketing-approach', ElementType.LINK)
    FINANCE = Selector(By.ID, 'sidebar-finance', ElementType.LINK)
    COSTS_AND_PRICING = Selector(By.ID, 'sidebar-costs-and-pricing', ElementType.LINK)
    PAYMENT_METHODS = Selector(By.ID, 'sidebar-payment-methods', ElementType.LINK)
    TRAVEL_AND_BUSINESS_POLICIES = Selector(By.ID, 'sidebar-travel-and-business-policies', ElementType.LINK)
    BUSINESS_RISK = Selector(By.ID, 'sidebar-business-risk', ElementType.LINK)
    ACTION_PLAN = Selector(By.ID, 'sidebar-action-plan', ElementType.LINK)
    CONTENT = Selector(By.ID, 'target-markets-content')


class ExportPlanTargetMarketsRecommendedCountriesFolded(SelectorsEnum):
    RECOMMENDED_COUNTRIES = Selector(By.ID, 'recommended-countries')
    SECTOR_CHOOSER_BUTTON = Selector(By.ID, 'sector-chooser-button', ElementType.BUTTON)


class ExportPlanTargetMarketsRecommendedCountriesUnfolded(SelectorsEnum):
    SECTOR_LIST = Selector(By.ID, 'sector-list')


class ExportPlanTargetMarketsData(SelectorsEnum):
    MARKET_DATA = Selector(By.CSS_SELECTOR, 'section[id^=export-market-data]')
    REMOVE_COUNTR = Selector(By.ID, 'remove-country')
    EASE_OF_DOING_BUSINESS = Selector(By.ID, 'export-market-data-ease-of-doing-business-rank')
    CPI = Selector(By.ID, 'export-market-data-corruption-perception-index')
    LOCAL_TIME = Selector(By.ID, 'export-market-data-local-time')
    DUTY = Selector(By.ID, 'export-market-data-duty')
    IMPORT_VALUE = Selector(By.ID, 'export-market-data-import-value')
    YEAR_TO_YEAR_CHANGE = Selector(By.ID, 'export-market-data-year-to-year-change')
    ADD_COUNTRY = Selector(By.ID, 'country-chooser-button')
    YOUR_ACTIONS = Selector(By.ID, 'your-actions')


class TopicLessonListing(SelectorsEnum):
    TITLE = Selector(By.ID, 'topic-title')
    LESSON_LIST = Selector(By.ID, 'topic-lesson-list')
    LESSON_LINKS = Selector(By.CSS_SELECTOR, 'a[id^=lesson-]')


class LessonPage(SelectorsEnum):
    TITLE = Selector(By.ID, 'lesson-title')
    MARK_AS_READ = Selector(By.ID, 'mark-as-read')
