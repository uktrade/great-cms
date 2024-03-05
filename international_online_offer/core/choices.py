from international_online_offer.core import (
    hirings,
    intents,
    landing_timeframes,
    regions,
    spends,
)

INTENT_CHOICES = (
    (intents.SET_UP_NEW_PREMISES, 'Set up new premises'),
    (intents.SET_UP_A_NEW_DISTRIBUTION_CENTRE, 'Set up a new distribution centre'),
    (intents.ONWARD_SALES_AND_EXPORTS_FROM_THE_UK, 'Onward sales and exports from the UK'),
    (intents.RESEARCH_DEVELOP_AND_COLLABORATE, 'Research, develop and collaborate'),
    (intents.FIND_PEOPLE_WITH_SPECIALIST_SKILLS, 'Find people with specialist skills'),
    (intents.OTHER, 'Other'),
)

# Copy of EXPERTISE_REGION_CHOICES in directory constants but using non const keys needed for scorecard service
REGION_CHOICES = (
    (regions.EAST_OF_ENGLAND, 'East of England'),
    (regions.EAST_MIDLANDS, 'East Midlands'),
    (regions.LONDON, 'London'),
    (regions.NORTH_EAST, 'North East'),
    (regions.NORTH_WEST, 'North West'),
    (regions.NORTHERN_IRELAND, 'Northern Ireland'),
    (regions.SCOTLAND, 'Scotland'),
    (regions.SOUTH_EAST, 'South East'),
    (regions.SOUTH_WEST, 'South West'),
    (regions.WALES, 'Wales'),
    (regions.WEST_MIDLANDS, 'West Midlands'),
    (regions.YORKSHIRE_AND_THE_HUMBER, 'Yorkshire and the Humber'),
)


HIRING_CHOICES = (
    (hirings.ONE_TO_TEN, '1 to 10'),
    (hirings.ELEVEN_TO_FIFTY, '11 to 50'),
    (hirings.FIFTY_ONE_TO_ONE_HUNDRED, '51 to 100'),
    (hirings.ONE_HUNDRED_ONE_PLUS, 'More than 100'),
    (hirings.NO_PLANS_TO_HIRE_YET, 'No plans to hire yet'),
)

SPEND_CHOICES = (
    (spends.LESS_THAN_TEN_THOUSAND, 'Less than £10,000'),
    (spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND, '£10,000 to £500,000'),
    (spends.FIVE_HUNDRED_THOUSAND_TO_ONE_MILLION, '£500,000 to £1 million'),
    (spends.ONE_MILLION_TO_TWO_MILLION, '£1 million to £2 million'),
    (spends.TWO_MILLION_TO_FIVE_MILLION, '£2 million to £5 million'),
    (spends.FIVE_MILLION_TO_TEN_MILLION, '£5 million to £10 million'),
    (spends.MORE_THAN_TEN_MILLION, 'More than £10 million'),
)

SPEND_CHOICES_EURO = (
    (spends.LESS_THAN_TEN_THOUSAND, 'Less than €11.000'),
    (spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND, '€11.000 to €570.000'),
    (spends.FIVE_HUNDRED_THOUSAND_TO_ONE_MILLION, '€570.000 to €1,1 million'),
    (spends.ONE_MILLION_TO_TWO_MILLION, '€1,1 million to €2,2 million'),
    (spends.TWO_MILLION_TO_FIVE_MILLION, '€2,2 million to €5,7 million'),
    (spends.FIVE_MILLION_TO_TEN_MILLION, '€5,7 million to €11 million'),
    (spends.MORE_THAN_TEN_MILLION, 'More than €11 million'),
)

SPEND_CHOICES_USD = (
    (spends.LESS_THAN_TEN_THOUSAND, 'Less than $12,000'),
    (spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND, '$12,000 to $600,000'),
    (spends.FIVE_HUNDRED_THOUSAND_TO_ONE_MILLION, '$600,000 to $1.2 million'),
    (spends.ONE_MILLION_TO_TWO_MILLION, '$1.2 million to $2.4 million'),
    (spends.TWO_MILLION_TO_FIVE_MILLION, '$2.4 million to $6 million'),
    (spends.FIVE_MILLION_TO_TEN_MILLION, '$6 million to $12 million'),
    (spends.MORE_THAN_TEN_MILLION, 'More than $12 million'),
)

SPEND_CURRENCY_CHOICES = (
    ('GBP', 'Pound sterling (GBP)'),
    ('EUR', 'Euro (EUR)'),
    ('USD', 'United States Dollar (USD)'),
)

LANDING_TIMEFRAME_CHOICES = (
    (landing_timeframes.UNDER_SIX_MONTHS, 'Under 6 months'),
    (landing_timeframes.SIX_TO_TWELVE_MONTHS, '6 - 12 months'),
    (landing_timeframes.ONE_TO_TWO_YEARS, '1 - 2 years'),
    (landing_timeframes.OVER_TWO_YEARS, 'Over 2 years'),
)

SATISFACTION_CHOICES = (
    ('VERY_SATISFIED', 'Very satisfied'),
    ('SATISFIED', 'Satisfied'),
    ('NEITHER', 'Neither satisfied nor dissatisfied'),
    ('DISSATISFIED', 'Dissatisfied'),
    ('VERY_DISSATISFIED', 'Very dissatisfied'),
)

EXPERIENCE_CHOICES = (
    ('I_DID_NOT_EXPERIENCE_ANY_ISSUE', 'I did not experience any issue'),
    ('I_DID_NOT_FIND_WHAT_I_WAS_LOOKING_FOR', 'I did not find what I was looking for'),
    ('I_FOUND_IT_DIFFICULT_TO_NAVIGATE_THE_SITE', 'I found it difficult to navigate the site'),
    ('THE_SYSTEM_LACKS_THE_FEATURE_I_NEED', 'The system lacks the feature I need'),
    ('I_WAS_UNABLE_TO_LOAD_REFRESH_ENTER_A_PAGE', 'I was unable to load/refresh/enter a page'),
    ('OTHER', 'Other'),
)

LIKELIHOOD_CHOICES = (
    ('EXTREMELY_LIKELY', 'Extremely likely'),
    ('LIKELY', 'Likely'),
    ('NEITHER_LIKELY_NOR_UNLIKELY', 'Neither likely nor unlikely'),
    ('UNLIKELY', 'Unlikely'),
    ('EXTREMELY_UNLIKELY', 'Extremely unlikely'),
    ('DONT_KNOW_OR_PREFER_NOT_TO_SAY', "Don't know / prefer not to say"),
)

INTENSION_CHOICES = (
    ('HELP_US_SET_UP_IN_THE_UK', 'Help us set up in the UK'),
    ('UNDERSTAND_THE_UK_LEGAL_SYSTEM', 'Understand the UK legal system such as tax and employment regulations'),
    ('PUT_US_IN_TOUCH_WITH_EXPERTS', 'Put us in touch with experts to help us set up'),
    ('ACCESS_TRUSTED_INFORMATION', 'Access trusted information'),
    ('LEARN_ABOUT_AVAILABLE_INCENTIVES', 'Learn about available incentives'),
    ('DONT_KNOW_OR_PREFER_NOT_TO_SAY', "Don't know / prefer not to say"),
    ('MY_BUSINESS_WILL_NOT_USE_THE_SITE', 'My business will not use the site'),
    ('OTHER', 'Other'),
)
