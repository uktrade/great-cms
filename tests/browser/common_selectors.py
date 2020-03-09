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


class Header(SelectorsEnum):
    HEADER_SECTION = Selector(By.ID, 'header', ElementType.HEADER)
    LOGO_LINK = Selector(By.ID, 'header-logo-link', ElementType.LINK)
    LOGO = Selector(By.ID, 'header-logo-exporting-is-great', ElementType.IMAGE)
    SERVICES_AREA = Selector(By.ID, 'services-area', ElementType.UL)
    LEARNING = Selector(By.ID, 'header-link-learning', ElementType.LINK)
    EXPORTING_PLAN = Selector(By.ID, 'header-link-exporting-plan', ElementType.LINK)
    MARKETS = Selector(By.ID, 'header-link-markets', ElementType.LINK)
    SERVICES = Selector(By.ID, 'header-link-services', ElementType.LINK)
    USER_STAGE_AREA = Selector(By.ID, 'user-state-area', ElementType.UL)
    NOTIFICATIONS = Selector(
        By.ID, 'header-link-notifications', ElementType.LINK, is_authenticated=True
    )
    USER_PROFILE = Selector(
        By.ID, 'header-link-user-profile', ElementType.LINK, is_authenticated=True
    )
    USER_PROFILE_EMAIL = Selector(
        By.ID, 'header-link-user-profile-email-link', ElementType.LINK, is_authenticated=True
    )
    DASHBOARD = Selector(
        By.ID, 'header-link-dashboard', ElementType.LINK, is_authenticated=True
    )
    SIGN_IN = Selector(By.ID, 'header-sign-in-link', ElementType.LINK)
    SIGN_UP = Selector(
        By.ID, 'header-sign-up-link', ElementType.LINK, is_authenticated=True
    )


class SignUpModal(SelectorsEnum):
    MODAL = Selector(By.ID, 'signup-modal')
    LINKEDIN = Selector(By.ID, 'signup-modal-linkedin')
    GOOGLE = Selector(By.ID, 'signup-modal-google')
    LOG_IN = Selector(By.ID, 'signup-modal-log-in')
    T_AND_C = Selector(By.ID, 'signup-modal-t-and-c')
    SUBMIT = Selector(By.ID, 'signup-modal-submit', ElementType.BUTTON)
    EMAIL = Selector(By.ID, 'id_email', ElementType.INPUT)
    PASSWORD = Selector(By.ID, 'id_password', ElementType.INPUT)
