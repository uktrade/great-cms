DYNAMIC_SNIPPET_NAMES = (
    ('BGS_5_004', 'Finance and support for your business'),
    ('BGS_5_006', 'British Business Bank Regional funds'),
    ('BGS_5_010', 'Find a grant'),
    ('BGS_6_001', 'Innovate UK Catapult Network'),
    ('BGS_6_002', 'Innovate UK Business Connect'),
    ('BGS_9_021', 'Apprenticeships placeholder'),
    ('BGS_12_005', 'Talk to an International Trade Adviser'),
    ('BGS_13_001', 'Contracts finder'),
    ('BGS_15_001', 'Scottish Enterprise'),
    ('BGS_15_002', 'Highlands & Islands Enterprise'),
    ('BGS_15_003', 'South of Scotland Enterprise'),
)

DYNAMIC_CHILD_PAGE_CHOICES = [
    ('interested_in_exporting', 'Interested in exporting'),
    ('not_interested_in_exporting', 'Not interested in exporting'),
]

CARD_META_DATA = (
    ('www.gov.uk', 'GOV.UK', 'govuk'),
    ('www.british-business-bank.co.uk', 'british-business-bank.co.uk', 'british-business-bank'),
    ('smallbusinesscharter.org', 'smallbusinesscharter.org', 'small-business-charter'),
)

PRE_START_GUIDE_URL = '/support-in-uk/pre-start-guide/'
START_UP_GUIDE_URL = '/support-in-uk/start-up-guide/'
ESTABLISHED_GUIDE_URL = '/support-in-uk/established-guide/'
PRE_START_BUSINESS_TYPE = 'pre_start'
ESTABLISHED_OR_START_UP_BUSINESS_TYPE = 'established_or_startup'
PRE_START_TRIAGE_URL = '/support-in-uk/pre-start/location/'
EXISTING_TRIAGE_URL = '/support-in-uk/existing/location/'

REGION_IMAGES = (
    ('North East', 'bgs-section-logo--north-east'),
    ('North West', 'bgs-section-logo--north-west'),
    ('Yorkshire and The Humber', 'bgs-section-logo--yorkshire'),
    ('East Midlands', 'bgs-section-logo--east-midlands'),
    ('West Midlands', 'bgs-section-logo--west-midlands'),
    ('East of England', 'bgs-section-logo--east-of-england'),
    ('London', 'bgs-section-logo--london'),
    ('South East', 'bgs-section-logo--south-east'),
    ('South West', 'bgs-section-logo--south-west'),
    ('Scotland', 'bgs-section-logo--scotland'),
    ('Wales', 'bgs-section-logo--wales'),
    ('Northern Ireland', 'bgs-section-logo--northern-ireland'),
)

FINANCE_AND_SUPPORT_REGION_MAPPINGS = (
    ('North East', 'north-east'),
    ('North West', 'north-west'),
    ('Yorkshire and The Humber', 'yorkshire-and-the-humber'),
    ('East Midlands', 'east-midlands'),
    ('West Midlands', 'west-midlands'),
    ('East of England', 'eastern'),
    ('London', 'london'),
    ('South East', 'south-east'),
    ('South West', 'south-west'),
    ('Scotland', 'scotland'),
    ('Wales', 'wales'),
    ('Northern Ireland', 'northern-ireland'),
)

FIND_A_GRANT_MAPPINGS = (
    ('North East', '4'),
    ('North West', '5'),
    ('Yorkshire and The Humber', '3'),
    ('East Midlands', '8'),
    ('West Midlands', '8'),
    ('East of England', '3'),
    ('London', '3'),
    ('South East', '6'),
    ('South West', '7'),
    ('Scotland', '9'),
    ('Wales', '10'),
    ('Northern Ireland', '11'),
)

ITA_EXCLUED_TURNOVERS = ('LESS_THAN_90K', '90K_TO_500K', 'PREFER_NOT_TO_SAY')

SCOTTISH_ENTERPRISE_ADMIN_DISTRICTS = (
    'Aberdeen City',
    'Aberdeenshire',
    'Angus',
    'City of Edinburgh',
    'Clackmannanshire',
    'Dundee City',
    'East Lothian',
    'Falkirk',
    'Fife',
    'Midlothian',
    'North Lanarkshire',
    'Perth and Kinross',
    'South Ayrshire',
    'Stirling',
    'West Lothian',
)

HIGHLANDS_AND_ISLANDS_ADMIN_DISTRICTS = (
    'Argyll and Bute',
    'Highland',
    'Moray',
    'Na h-Eileanan Siar',
    'Orkney Islands',
    'Shetland Islands',
)

SOUTH_OF_SCOTLAND_ENTERPRISES_ADMIN_DISTRICTS = (
    'Dumfries and Galloway',
    'Scottish Borders',
)

INTERNAL_GREAT_DOMAIN = 'great.gov.uk'

INTERNAL_BUSINESS_DOMAIN = 'business.gov.uk'
