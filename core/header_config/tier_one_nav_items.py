from django.utils.translation import gettext_lazy as _

from core.header_config.helpers import NavItem
from directory_constants import urls

INVEST_IN_THE_UK_URL = urls.international.HOME / 'investment/'
FIND_UK_SPECIALIST = urls.international.HOME / 'investment-support-directory/'
INTERNATIONAL_CONTACT = urls.international.HOME / 'contact/'


ABOUT_UK = NavItem(name='about-uk', title=_('About the UK'), url=urls.international.ABOUT_UK_HOME)

EXPAND = NavItem(name='expand', title=_('Expand to the UK'), url=urls.international.EXPAND_HOME)

INVEST_CAPITAL = NavItem(
    name='invest-capital', title=_('Invest capital in the UK'), url=urls.international.CAPITAL_INVEST_HOME
)

BUY_FROM_THE_UK = NavItem(name='trade', title=_('Buy from the UK'), url=urls.international.TRADE_HOW_WE_HELP)

ABOUT_DIT = NavItem(name='about-us', title=_('About us'), url=urls.international.ABOUT_DIT_HOME)

INVEST_IN_UK = NavItem(name='invest-in-the-uk', title=_('Invest in the UK'), url=INVEST_IN_THE_UK_URL)

FIND_UK_SPECIALIST = NavItem(name='find-a-uk-specialist', title=_('Find a UK Specialist'), url=FIND_UK_SPECIALIST)

CONTACT = NavItem(name='contact', title=_('Contact'), url=INTERNATIONAL_CONTACT)
