from directory_constants import sectors as directory_constants_sectors
from international_online_offer.core import (
    hirings,
    intents,
    landing_timeframes,
    regions,
    sectors,
    spends,
)

# Mix of existing sectors in directory constants but also new ones passed on for this apps needs
SECTOR_CHOICES = (
    (sectors.ADVANCED_ENGINEERING, 'Advanced engineering'),
    (directory_constants_sectors.AEROSPACE, 'Aerospace'),
    (
        directory_constants_sectors.AGRICULTURE_HORTICULTURE_AND_FISHERIES,
        'Agriculture, Horticulture, Fisheries and pets',
    ),
    (directory_constants_sectors.AIRPORTS, 'Airports'),
    (directory_constants_sectors.AUTOMOTIVE, 'Automotive'),
    (directory_constants_sectors.BIOTECHNOLOGY_AND_PHARMACEUTICALS, 'Biotech and Pharmaceuticals'),
    (directory_constants_sectors.BUSINESS_AND_CONSUMER_SERVICES, 'Business and consumer services'),
    (directory_constants_sectors.CHEMICALS, 'Chemicals'),
    (directory_constants_sectors.CONSTRUCTION, 'Construction'),
    (directory_constants_sectors.CONSUMER_AND_RETAIL, 'Consumer and retail'),
    (sectors.CREATIVE_INDUSTRIES, 'Creative industries'),
    (sectors.DEFENCE_AND_SECURITY, 'Defense and Security'),
    (directory_constants_sectors.EDUCATION_AND_TRAINING, 'Education and Training'),
    (directory_constants_sectors.ENERGY, 'Energy'),
    (directory_constants_sectors.ENVIRONMENT, 'Environment'),
    (directory_constants_sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES, 'Financial and Professional Services'),
    (directory_constants_sectors.FOOD_AND_DRINK, 'Food and Drink'),
    (directory_constants_sectors.HEALTHCARE_AND_MEDICAL, 'Healthcare and Medical'),
    (sectors.INFRASTRUCTURE_AIR_AND_SEA, 'Infrastructure Air and Sea'),
    (sectors.LEISURE, 'Leisure'),
    (sectors.LOGISTICS, 'Logistics'),
    (sectors.MANUFACTURING, 'Manufacturing'),
    (directory_constants_sectors.MARINE, 'Marine'),
    (sectors.MARITIME_SERVICES, 'Maritime Services'),
    (sectors.MEDICAL_DEVICES_AND_EQUIPMENT, 'Medical devices and equipment'),
    (directory_constants_sectors.MINING, 'Mining'),
    (sectors.NUCLEAR, 'Nuclear'),
    (directory_constants_sectors.OIL_AND_GAS, 'Oil and Gas'),
    (sectors.RAIL, 'Rail'),
    (directory_constants_sectors.RENEWABLE_ENERGY, 'Renewable'),
    (sectors.RETAIL, 'Retail'),
    (directory_constants_sectors.SECURITY, 'Security'),
    (sectors.SPACE, 'Space'),
    (sectors.SPORTS_EVENTS, 'Sports Events'),
    (sectors.TECHNOLOGY_AND_SMART_CITIES, 'Technology and Smart Cities'),
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
    (regions.EASTERN, 'East'),
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
    (regions.YORKSHIRE_AND_HUMBER, 'Yorkshire and the Humber'),
)


HIRING_CHOICES = (
    (hirings.ONE_TO_TEN, '1 to 10'),
    (hirings.ELEVEN_TO_FIFTY, '11 to 50'),
    (hirings.FIFTY_ONE_TO_ONE_HUNDRED, '51 to 100'),
    (hirings.ONE_HUNDRED_ONE_PLUS, 'More than 100'),
    (hirings.NO_PLANS_TO_HIRE_YET, 'No plans to hire yet'),
)

SPEND_CHOICES = (
    (spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND, '£10,000 - £500,000'),
    (spends.FIVE_HUNDRED_THOUSAND_ONE_TO_ONE_MILLION, '£500,000 - £1,000,000'),
    (spends.ONE_MILLION_ONE_TO_TWO_MILLION, '£1,000,001 - £2,000,000'),
    (spends.TWO_MILLION_ONE_TO_FIVE_MILLION, '£2,000,001 - £5,000,000'),
    (spends.FIVE_MILLION_ONE_TO_TEN_MILLION, '£5,000,001 - £10,000,000'),
    (spends.TEN_MILLION_ONE_PLUS, 'More than £10 million'),
    (spends.SPECIFIC_AMOUNT, 'Specific amount'),
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
