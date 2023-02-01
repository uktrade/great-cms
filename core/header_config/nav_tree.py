from collections import namedtuple

from . import old_nav_items, tier_one_nav_items, tier_two_nav_items

NavNode = namedtuple('NavNode', 'tier_one_item tier_two_items')

OLD_HEADER_TREE = [
    NavNode(tier_one_item=old_nav_items.INVEST, tier_two_items=[]),
    NavNode(tier_one_item=old_nav_items.HOW_TO_SETUP, tier_two_items=[]),
    NavNode(tier_one_item=old_nav_items.FAS, tier_two_items=[]),
    NavNode(tier_one_item=old_nav_items.INDUSTRIES, tier_two_items=[]),
]

HEADER_TREE = [
    NavNode(
        tier_one_item=tier_one_nav_items.ABOUT_UK,
        tier_two_items=[
            tier_two_nav_items.OVERVIEW_ABOUT,
            tier_two_nav_items.WHY_CHOOSE_THE_UK,
            tier_two_nav_items.INDUSTRIES,
            tier_two_nav_items.REGIONS,
            tier_two_nav_items.CONTACT_US_ABOUT_UK,
        ],
    ),
    NavNode(
        tier_one_item=tier_one_nav_items.EXPAND,
        tier_two_items=[
            tier_two_nav_items.OVERVIEW_EXPAND,
            tier_two_nav_items.HOW_WE_HELP_EXPAND,
            tier_two_nav_items.HOW_TO_EXPAND,
            tier_two_nav_items.INVESTMENT_SUPPORT_DIRECTORY,
            tier_two_nav_items.CONTACT_US_EXPAND,
        ],
    ),
    NavNode(
        tier_one_item=tier_one_nav_items.INVEST_CAPITAL,
        tier_two_items=[
            tier_two_nav_items.OVERVIEW_INVEST_CAPITAL,
            tier_two_nav_items.HOW_WE_HELP_CAPITAL_INVEST,
            tier_two_nav_items.INVESTMENT_OPPORTUNITIES,
            tier_two_nav_items.CONTACT_US_INVEST_CAPITAL,
        ],
    ),
    NavNode(
        tier_one_item=tier_one_nav_items.BUY_FROM_THE_UK,
        tier_two_items=[
            tier_two_nav_items.HOW_WE_HELP_BUY,
            tier_two_nav_items.FIND_A_SUPPLIER,
            tier_two_nav_items.CONTACT_US_TRADE,
        ],
    ),
    NavNode(
        tier_one_item=tier_one_nav_items.ABOUT_DIT,
        tier_two_items=[
            tier_two_nav_items.OVERVIEW_ABOUT_DIT,
            tier_two_nav_items.CONTACT_US_ABOUT_DIT,
        ],
    ),
]

ATLAS_HEADER_TREE = [
    NavNode(
        tier_one_item=tier_one_nav_items.INVEST_IN_UK,
        tier_two_items=[
            tier_two_nav_items.WHY_INVEST_IN_UK,
            tier_two_nav_items.REGIONS,
            tier_two_nav_items.SECTORS,
            tier_two_nav_items.INVESTMENT_OPPORTUNITIES,
            tier_two_nav_items.HOW_WE_CAN_HELP_INVESTMENT_ATLAS,
        ],
    ),
    NavNode(
        tier_one_item=tier_one_nav_items.BUY_FROM_THE_UK,
        tier_two_items=[
            tier_two_nav_items.HOW_WE_HELP_BUY,
            tier_two_nav_items.FIND_A_SUPPLIER,
            tier_two_nav_items.CONTACT_US_TRADE,
        ],
    ),
    NavNode(tier_one_item=tier_one_nav_items.CONTACT, tier_two_items=[]),
]
