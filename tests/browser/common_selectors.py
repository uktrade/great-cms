# -*- coding: utf-8 -*-
from enum import Enum
from typing import NamedTuple

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
        return getattr(self.value, 'name', None) or self.__class__.__name__

    __repr__ = __str__


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


class Selector(NamedTuple):
    by: By
    selector: str
    type: ElementType = None
    is_visible: bool = True
    is_authenticated: bool = False
    name: str = None
    selector_template: str = None

    def __str__(self) -> str:
        return self.name or self.__class__.__name__

    __repr__ = __str__


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
    USER_PROFILE = Selector(By.ID, 'header-link-user-profile', type=ElementType.LINK)


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
    TOPICS_HEADERS = Selector(By.CSS_SELECTOR, '#your-progress-card h3[id^=topics-]')
    TOPICS_READ_PROGRESS = Selector(By.CSS_SELECTOR, '#your-progress-card .progress-bar-text')
    LESSONS_COMPLETED_TEXT = Selector(By.ID, 'lessons-completed-text')


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


class PersonalisationBar(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'personalisation-bar')
    PRODUCT = Selector(By.ID, 'set-product-button')
    COUNTRY = Selector(By.ID, 'set-country-button')


class ExportPlanDashboard(SelectorsEnum):
    ABOUT_YOUR_BUSINESS = Selector(By.ID, 'about-your-business', type=ElementType.LINK)
    OBJECTIVES = Selector(By.ID, 'objectives', type=ElementType.LINK)
    TARGET_MARKETS_RESEARCH = Selector(By.ID, 'target-markets-research', type=ElementType.LINK)
    ADAPTATION = Selector(By.ID, 'adapting-your-product', type=ElementType.LINK)
    MARKETING_APPROACH = Selector(By.ID, 'marketing-approach', type=ElementType.LINK)
    COSTS_AND_PRICING = Selector(By.ID, 'costs-and-pricing', type=ElementType.LINK)
    FINANCE = Selector(By.ID, 'finance', type=ElementType.LINK)
    PAYMENT_METHODS = Selector(By.ID, 'payment-methods', type=ElementType.LINK)
    TRAVEL_AND_BUSINESS_POLICIES = Selector(By.ID, 'travel-and-business-policies', type=ElementType.LINK)
    BUSINESS_RISK = Selector(By.ID, 'business-risk', type=ElementType.LINK)


class ExportPlanTargetMarketsResearch(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'sidebar-content')
    ABOUT_YOUR_BUSINESS = Selector(By.ID, 'sidebar-about-your-business', type=ElementType.LINK)
    OBJECTIVES = Selector(By.ID, 'sidebar-objectives', type=ElementType.LINK)
    TARGET_MARKETS_RESEARCH = Selector(By.ID, 'sidebar-target-markets-research', type=ElementType.LINK)
    ADAPTATION = Selector(By.ID, 'sidebar-adapting-your-product', type=ElementType.LINK)
    MARKETING_APPROACH = Selector(By.ID, 'sidebar-marketing-approach', type=ElementType.LINK)
    COSTS_AND_PRICING = Selector(By.ID, 'sidebar-costs-and-pricing', type=ElementType.LINK)
    FINANCE = Selector(By.ID, 'sidebar-finance', type=ElementType.LINK)
    PAYMENT_METHODS = Selector(By.ID, 'sidebar-payment-methods', type=ElementType.LINK)
    TRAVEL_AND_BUSINESS_POLICIES = Selector(By.ID, 'sidebar-travel-and-business-policies', type=ElementType.LINK)
    BUSINESS_RISK = Selector(By.ID, 'sidebar-business-risk', type=ElementType.LINK)
    CONTENT = Selector(By.ID, 'target-markets-research-content')


class TargetMarketsRecommendedCountries(SelectorsEnum):
    CONTAINER = Selector(By.ID, 'recommended-countries')
    COUNTRY_LIST = Selector(By.ID, 'recommended-countries-list')
    COUNTRY_BUTTONS = Selector(By.CSS_SELECTOR, '#recommended-countries-list button')


class TopicLessonListing(SelectorsEnum):
    TITLE = Selector(By.CLASS_NAME, 'great-ds-hero__heading')
    LESSON_LIST = Selector(By.ID, 'topic-lesson-list')
    LESSON_LINKS = Selector(By.CSS_SELECTOR, 'li[id^=lesson-]')


class LessonPage(SelectorsEnum):
    TITLE = Selector(By.ID, 'lesson-title')
