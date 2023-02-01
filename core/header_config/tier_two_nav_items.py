from django.utils.translation import gettext_lazy as _

from core.header_config.helpers import NavItem
from directory_constants import urls

# Until we can update directory-constants, define this just here
WHY_INVEST_IN_THE_UK_URL = urls.international.HOME / 'content/investment/why-invest-in-the-uk'
REGIONS_URL = urls.international.HOME / 'content/investment/regions/'
SECTORS_URL = urls.international.HOME / 'content/investment/sectors/'
INVESTMENT_OPPORTUNITIES_URL = urls.international.HOME / 'investment/opportunities/'
ATLAS_HOW_WE_CAN_HELP_URL = urls.international.HOME / 'content/investment/how-we-can-help/'


OVERVIEW_ABOUT = NavItem(name='overview-about-uk', title=_('Overview'), url=urls.international.ABOUT_UK_HOME)

WHY_CHOOSE_THE_UK = NavItem(
    name='why-choose-the-uk', title=_('Why choose the UK'), url=urls.international.ABOUT_UK_WHY_CHOOSE_UK
)

INDUSTRIES = NavItem(name='industries', title=_('Industries'), url=urls.international.ABOUT_UK_INDUSTRIES)

CONTACT_US_ABOUT_UK = NavItem(
    name='contact-us-about-uk', title=_('Contact us'), url=urls.international.ABOUT_UK_CONTACT
)

OVERVIEW_EXPAND = NavItem(name='overview-expand', title=_('Overview'), url=urls.international.EXPAND_HOME)

HOW_TO_EXPAND = NavItem(
    name='how-to-expand', title=_('How to expand to the UK'), url=urls.international.EXPAND_HOW_TO_SETUP
)

INVESTMENT_SUPPORT_DIRECTORY = NavItem(
    name='investment-support-directory', title=_('Find a UK specialist'), url=urls.international.EXPAND_ISD_HOME
)

HOW_WE_HELP_EXPAND = NavItem(
    name='how-we-help-expand', title=_('How we help'), url=urls.international.EXPAND_HOW_WE_HELP
)

CONTACT_US_EXPAND = NavItem(name='contact-us-expand', title=_('Contact us'), url=urls.international.EXPAND_CONTACT)

OVERVIEW_INVEST_CAPITAL = NavItem(
    name='overview-invest-capital', title=_('Overview'), url=urls.international.CAPITAL_INVEST_HOME
)

# This page does not yet exist - will 404 for now.
INVESTMENT_TYPES = NavItem(
    name='investment-types',
    title=_('Investment types'),
    url=urls.international.CAPITAL_INVEST_HOME / 'investment-types',
)

# This page does not yet exist - will 404 for now.
HOW_TO_INVEST_CAPITAL = NavItem(
    name='how-to-invest-capital',
    title=_('How to invest capital'),
    url=urls.international.CAPITAL_INVEST_HOME / 'how-to-invest-capital',
)

HOW_WE_HELP_CAPITAL_INVEST = NavItem(
    name='how-we-help-invest', title=_('How we help'), url=urls.international.CAPITAL_INVEST_HOW_WE_HELP
)

CONTACT_US_INVEST_CAPITAL = NavItem(
    name='contact-us-invest-capital', title=_('Contact us'), url=urls.international.CAPITAL_INVEST_CONTACT
)

FIND_A_SUPPLIER = NavItem(name='find-a-supplier', title=_('Find a supplier'), url=urls.international.TRADE_FAS)

# This page does not yet exist - will 404 for now.
HOW_TO_TRADE = NavItem(
    name='how-to-trade', title=_('How to buy from the UK'), url=urls.international.TRADE_HOME / 'how-to-trade'
)

HOW_WE_HELP_BUY = NavItem(name='how-we-help-buy', title=_('How we help'), url=urls.international.TRADE_HOW_WE_HELP)

CONTACT_US_TRADE = NavItem(name='contact-us-trade', title=_('Contact us'), url=urls.international.TRADE_CONTACT)

OVERVIEW_ABOUT_DIT = NavItem(name='overview-about-dit', title=_('Overview'), url=urls.international.ABOUT_DIT_HOME)

CONTACT_US_ABOUT_DIT = NavItem(
    name='contact-us-about-dit', title=_('Contact us'), url=urls.international.ABOUT_DIT_CONTACT
)

WHY_INVEST_IN_UK = NavItem(name='why-invest-in-the-uk', title=_('Why invest in the UK?'), url=WHY_INVEST_IN_THE_UK_URL)

REGIONS = NavItem(name='regions', title=_('UK nations and regions'), url=REGIONS_URL)

SECTORS = NavItem(name='sectors', title=_('Sectors'), url=SECTORS_URL)

INVESTMENT_OPPORTUNITIES = NavItem(
    name='investment-opportunities', title=_('Investment opportunities'), url=INVESTMENT_OPPORTUNITIES_URL
)

HOW_WE_CAN_HELP_INVESTMENT_ATLAS = NavItem(
    name='how-we-can-help', title=_('How we can help'), url=ATLAS_HOW_WE_CAN_HELP_URL
)
