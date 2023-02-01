from django.utils.translation import gettext_lazy as _

from core.header_config.helpers import NavItem
from directory_constants import urls

INVEST = NavItem(name='old-invest', title=_('Invest'), url=urls.international.EXPAND_HOME)

HOW_TO_SETUP = NavItem(name='old-setup-up-guide', title=_('UK setup guide'), url=urls.international.EXPAND_HOW_TO_SETUP)

FAS = NavItem(name='old-fas', title=_('Find a UK supplier'), url=urls.international.TRADE_HOME)

INDUSTRIES = NavItem(name='old-industries', title=_('Industries'), url=urls.international.ABOUT_UK_INDUSTRIES)
