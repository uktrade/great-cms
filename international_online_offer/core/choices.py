from directory_constants import sectors as directory_constants_sectors
from international_online_offer.core import hirings, intents, regions, sectors, spends

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
    (regions.EASTERN, 'East of England'),
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
