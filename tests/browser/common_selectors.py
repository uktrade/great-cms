# -*- coding: utf-8 -*-
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

    @property
    def selector_template(self):
        return self.value.selector_template

    def __str__(self) -> str:
        return self.value.name if self.value.name else self.name

    def __repr__(self) -> str:
        return self.value.name if self.value.name else self.name


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

    def __str__(self) -> str:
        return self.value


class Selector(
    namedtuple('Selector', ['by', 'selector', 'type', 'is_visible', 'is_authenticated', 'name', 'selector_template'])
):
    __slots__ = ()

    def __new__(
        cls,
        by: By,
        selector: str,
        *,
        type: ElementType = None,
        is_visible: bool = True,
        is_authenticated: bool = False,
        name: str = None,
        selector_template: str = None,
    ):
        return super(Selector, cls).__new__(
            cls,
            by,
            selector=selector,
            type=type,
            is_visible=is_visible,
            is_authenticated=is_authenticated,
            name=name,
            selector_template=selector_template,
        )

    def __str__(self) -> str:
        return str(self.name) if self.name else str(self.__class__.__name__)

    def __repr__(self) -> str:
        return str(self.name) if self.name else str(self.__class__.__name__)


class HeaderCommon(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'header', type=ElementType.HEADER)
    LOGO_LINK = Selector(By.ID, 'header-logo-link', type=ElementType.LINK)
    LOGO = Selector(By.ID, 'header-logo-exporting-is-great', type=ElementType.IMAGE)
    SERVICES_AREA = Selector(By.ID, 'services-area', type=ElementType.UL)
    LEARNING = Selector(By.ID, 'header-link-learning', type=ElementType.LINK)
    EXPORTING_PLAN = Selector(By.ID, 'header-link-exporting-plan', type=ElementType.LINK)
    MARKETS = Selector(By.ID, 'header-link-markets', type=ElementType.LINK)
    SERVICES = Selector(By.ID, 'header-link-services', type=ElementType.LINK)
    USER_STATE_AREA = Selector(By.ID, 'user-state-area', type=ElementType.UL)


class HeaderSignUp(SelectorsEnum):
    SIGN_UP = Selector(By.ID, 'header-sign-up-link', type=ElementType.LINK)


class HeaderSignedIn(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'user-state-area', type=ElementType.HEADER, is_visible=False)
    NOTIFICATIONS = Selector(By.ID, 'header-link-notifications', type=ElementType.LINK)
    USER_PROFILE = Selector(By.ID, 'header-link-user-profile', type=ElementType.LINK)
    USER_PROFILE_EMAIL = Selector(By.ID, 'header-link-user-profile-email-link', type=ElementType.LINK)
    DASHBOARD = Selector(By.ID, 'header-link-dashboard', type=ElementType.LINK)


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
    SUBMIT = Selector(By.ID, 'signup-modal-submit', type=ElementType.BUTTON)
    EMAIL = Selector(By.ID, 'id_email', type=ElementType.INPUT)
    PASSWORD = Selector(By.ID, 'id_password', type=ElementType.INPUT)
    ERROR_MESSAGES = Selector(By.CSS_SELECTOR, 'li.error-message', is_visible=False)


class SignUpModalVerificationCode(SelectorsEnum):
    VERIFICATION_CODE = Selector(By.ID, 'id_code')
    SUBMIT_CODE = Selector(By.ID, 'signup-modal-submit-code', type=ElementType.BUTTON)


class SignUpModalSuccess(SelectorsEnum):
    MODAL = Selector(By.ID, 'signup-modal-success')
    SUBMIT = Selector(By.ID, 'signup-modal-submit-success', type=ElementType.BUTTON)


class DashboardModalLetsGetToKnowYou(SelectorsEnum):
    MODAL = Selector(By.ID, 'dashboard-question-modal-lets-get-to-know-you')
    INDUSTRIES_INPUT = Selector(By.ID, 'react-select-2-input', type=ElementType.INPUT)
    SUBMIT = Selector(By.ID, 'dashboard-question-modal-submit', type=ElementType.BUTTON)
    ERROR_MESSAGES = Selector(By.CSS_SELECTOR, 'li.error-message', is_visible=False)


class MarketsContainer(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'great-hero')
    BREADCRUMBS_HOME = Selector(By.ID, 'breadcrumbs-home', type=ElementType.LINK)
    BREADCRUMBS_MARKETS = Selector(By.CSS_SELECTOR, '#great-hero nav li span')
    CONTENT_CONTAINER = Selector(By.ID, 'markets-container')
    FORM = Selector(By.ID, 'markets-form')


class StickyHeader(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'exportplan-country-sector-customisation-bar')
    WHAT = Selector(By.ID, 'exportplan-country-sector-what')
    WHERE = Selector(By.ID, 'exportplan-country-sector-where')
    SHARE = Selector(By.ID, 'exportplan-collaboraton-menu-share', type=ElementType.LINK)
    DOWNLOAD = Selector(By.ID, 'exportplan-collaboraton-menu-download', type=ElementType.LINK)


class ExportPlanDashboard(SelectorsEnum):
    ABOUT_YOUR_BUSINESS = Selector(By.ID, 'about-your-business', type=ElementType.LINK)
    OBJECTIVES = Selector(By.ID, 'objectives', type=ElementType.LINK)
    TARGET_MARKETS = Selector(By.ID, 'target-markets', type=ElementType.LINK)
    ADAPTATION = Selector(By.ID, 'adaptation-for-international-markets', type=ElementType.LINK)
    MARKETING_APPROACH = Selector(By.ID, 'marketing-approach', type=ElementType.LINK)
    FINANCE = Selector(By.ID, 'finance', type=ElementType.LINK)
    COSTS_AND_PRICING = Selector(By.ID, 'costs-and-pricing', type=ElementType.LINK)
    PAYMENT_METHODS = Selector(By.ID, 'payment-methods', type=ElementType.LINK)
    TRAVEL_AND_BUSINESS_POLICIES = Selector(By.ID, 'travel-and-business-policies', type=ElementType.LINK)
    BUSINESS_RISK = Selector(By.ID, 'business-risk', type=ElementType.LINK)
    ACTION_PLAN = Selector(By.ID, 'action-plan', type=ElementType.LINK)


class ExportPlanDashboardPageTourStep0(SelectorsEnum):
    MODAL = Selector(By.ID, 'page-tour-modal-step-1')
    NEXT = Selector(By.ID, 'page-tour-submit', type=ElementType.LINK)
    SKIP = Selector(By.ID, 'page-tour-skip', type=ElementType.LINK)
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
    STEP = Selector(By.ID, 'page-tour-step-collaborate-with-your-team-and-international-trade-advisers',)
    HIGHLIGHTED_ELEMENT = Selector(By.ID, 'exportplan-collaboraton-menu')
    NEXT = Selector(By.ID, 'page-tour-next-step')


class ExportPlanDashboardPageTourStep5(SelectorsEnum):
    STEP = Selector(By.ID, 'page-tour-step-lets-start')
    HIGHLIGHTED_ELEMENT = Selector(By.ID, 'about-your-business')
    NEXT = Selector(By.ID, 'page-tour-start-now', type=ElementType.LINK)


class ExportPlanTargetMarkets(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'sidebar-content')
    ABOUT_YOUR_BUSINESS = Selector(By.ID, 'sidebar-about-your-business', type=ElementType.LINK)
    OBJECTIVES = Selector(By.ID, 'sidebar-objectives', type=ElementType.LINK)
    TARGET_MARKETS = Selector(By.ID, 'sidebar-target-markets', type=ElementType.LINK)
    ADAPTATION = Selector(By.ID, 'sidebar-adaptation-for-international-markets', type=ElementType.LINK)
    MARKETING_APPROACH = Selector(By.ID, 'sidebar-marketing-approach', type=ElementType.LINK)
    FINANCE = Selector(By.ID, 'sidebar-finance', type=ElementType.LINK)
    COSTS_AND_PRICING = Selector(By.ID, 'sidebar-costs-and-pricing', type=ElementType.LINK)
    PAYMENT_METHODS = Selector(By.ID, 'sidebar-payment-methods', type=ElementType.LINK)
    TRAVEL_AND_BUSINESS_POLICIES = Selector(By.ID, 'sidebar-travel-and-business-policies', type=ElementType.LINK)
    BUSINESS_RISK = Selector(By.ID, 'sidebar-business-risk', type=ElementType.LINK)
    ACTION_PLAN = Selector(By.ID, 'sidebar-action-plan', type=ElementType.LINK)
    CONTENT = Selector(By.ID, 'target-markets-content')


class TargetMarketsRecommendedCountriesFolded(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'target-market-countries-component')
    RECOMMENDED_COUNTRIES_SECTION = Selector(By.ID, 'recommended-countries')
    SECTOR_CHOOSER_SECTION = Selector(By.ID, 'sector-chooser')
    SECTOR_CHOOSER_BUTTON = Selector(By.ID, 'sector-chooser-button', type=ElementType.BUTTON)


class TargetMarketsSectorSelectorUnfolded(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'sector-chooser')
    SECTOR_LIST = Selector(By.ID, 'sector-list')
    SECTOR_BUTTONS = Selector(By.CSS_SELECTOR, '#sector-list button', type=ElementType.BUTTON)


class TargetMarketsSectorsSelected(SelectorsEnum):
    SAVE = Selector(By.ID, 'sector-list-save', type=ElementType.BUTTON)


class TargetMarketsSelectedSectors(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'sector-chooser')
    SECTORS = Selector(By.CSS_SELECTOR, '#selected-sectors li button')


class TargetMarketsRecommendedCountries(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'recommended-countries')
    COUNTRY_LIST = Selector(By.ID, 'recommended-countries-list')
    COUNTRY_BUTTONS = Selector(By.CSS_SELECTOR, '#recommended-countries-list button')


class ExportPlanTargetMarketsData(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'target-market-countries-component')
    MARKET_DATA = Selector(By.CSS_SELECTOR, 'section[id^=export-market-data--]')
    COUNTRY_NAME = Selector(By.CSS_SELECTOR, 'section[id^=export-market-data--] h2')
    REMOVE_COUNTRY = Selector(By.CLASS_NAME, 'remove-country-button')
    EASE_OF_DOING_BUSINESS = Selector(By.CSS_SELECTOR, 'div[id^=ease-of-doing-business-rank]')
    CPI = Selector(By.CSS_SELECTOR, 'div[id^=corruption-perception-index]')
    LOCAL_TIME = Selector(By.CSS_SELECTOR, 'div[id^=local-time-]')
    DUTY = Selector(By.CSS_SELECTOR, 'div[id^=duty-]')
    IMPORT_VALUE = Selector(By.CSS_SELECTOR, 'div[id^=import-value-]')
    YEAR_TO_YEAR_CHANGE = Selector(By.CSS_SELECTOR, 'div[id^=year-to-year-change-]')
    ADD_COUNTRY = Selector(By.ID, 'country-chooser-button')
    YOUR_ACTIONS = Selector(By.ID, 'your-actions')


class ExportPlanTargetMarketsDataTooltip(SelectorsEnum):
    EASE_OF_DOING_BUSINESS_TOOLTIP_BUTTON = Selector(
        By.CSS_SELECTOR, 'div[id^=ease-of-doing-business-rank] button', name='Ease of Doing Business tooltip button'
    )
    EASE_OF_DOING_BUSINESS_TOOLTIP = Selector(
        By.CSS_SELECTOR, 'div[id^=ease-of-doing-business-tooltip]', name='Ease of Doing Business tooltip'
    )
    CPI_TOOLTIP_BUTTON = Selector(
        By.CSS_SELECTOR, 'div[id^=corruption-perception-index] button', name='CPI tooltip button'
    )
    CPI_TOOLTIP = Selector(By.CSS_SELECTOR, 'div[id^=corruption-perception-index-tooltip]', name='CPI tooltip')


class TargetMarketsCountryChooser(SelectorsEnum):
    COUNTRY_AUTOCOMPLETE = Selector(By.ID, 'country-autocomplete')
    COUNTRY_AUTOCOMPLETE_MENU = Selector(By.CSS_SELECTOR, 'div.country-autocomplete__placeholder')
    AUTOCOMPLETE_COUNTRIES = Selector(By.CSS_SELECTOR, 'div[id^=react-select-2-option-]')
    SAVE_COUNTRY = Selector(By.ID, 'country-chooser-save-button')


class TopicLessonListing(SelectorsEnum):
    TITLE = Selector(By.ID, 'topic-title')
    LESSON_LIST = Selector(By.ID, 'topic-lesson-list')
    LESSON_LINKS = Selector(By.CSS_SELECTOR, 'a[id^=lesson-]')


class LessonPage(SelectorsEnum):
    TITLE = Selector(By.ID, 'lesson-title')
