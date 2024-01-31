SERVICE_NAME = 'great-cms'

VIDEO_DURATION_DATA_ATTR_NAME = 'data-v-duration'

BACKLINK_QUERYSTRING_NAME = 'return-link'

# Define a strict subset of rich-text features only includes linebreaks
RICHTEXT_FEATURES__MINIMAL = ()


# Define rich-text features that disable embeds, images and document links
RICHTEXT_FEATURES__REDUCED = [
    'anchor-identifier',
    'h2',
    'h3',
    'h4',
    # 'h5', 'h6'  # also available if we want, but be sure we do
    'bold',
    'italic',
    'ol',
    'ul',
    'hr',
    'link',
    'document-link',
    #  to allow links to Wagtail-held documents
    # 'blockquote', # NOT used - use a PullQuoteBlock in a StreamField, or similar
]

# For certain pages, we want them to be able to define their main page header, too
RICHTEXT_FEATURES__REDUCED__ALLOW_H1 = ['h1'] + RICHTEXT_FEATURES__REDUCED

# For certain pages, we want H2 disabled also (e.g. Description field in speakers snippet).
RICHTEXT_FEATURES__REDUCED__DISALLOW_H2 = [value for value in RICHTEXT_FEATURES__REDUCED if value != 'h2']

AWS_S3_MAIN_HOSTNAME_OPTIONS = [
    # https://docs.aws.amazon.com/general/latest/gr/s3.html
    's3.amazonaws.com',  # most likely
    's3.eu-west-2.amazonaws.com',  # London
    's3.dualstack.eu-west-2.amazonaws.com',  # London IPv4 + IPv6
    # 'account-id.s3-control.eu-west-2.amazonaws.com',  # inviable for us
    # 'account-id.s3-control.dualstack.eu-west-2.amazonaws.com',   # inviable for us
    's3-accesspoint.eu-west-2.amazonaws.com',
    's3-accesspoint.dualstack.eu-west-2.amazonaws.com',
]

ARTICLE_TYPES = [
    ('Blog', 'Blog'),
    ('Advice', 'Advice'),
    ('Case study', 'Case study'),
    ('Campaign', 'Campaign'),
]

CAMPAIGN_FORM_CHOICES = (
    ('Short', 'Short'),
    ('Long', 'Long'),
)

VIDEO_TRANSCRIPT_HELP_TEXT = 'If the video is present, a transcript must be provided.'

# Options for https://docs.wagtail.io/en/v2.8.1/reference/contrib/table_block.html
TABLEBLOCK_OPTIONS = {
    'minSpareRows': 0,
    'startRows': 3,
    'startCols': 2,
    'colHeaders': True,
    'rowHeaders': False,
    'contextMenu': True,
    'editor': 'text',
    'stretchH': 'all',
    'height': 108,  # optimised for 3 rows by default (ie, 1 row == 36px)
    'renderer': 'text',
    'autoColumnSize': False,
}

CONSENT_EMAIL = 'consents_to_email_contact'
CONSENT_PHONE = 'consents_to_phone_contact'

CONSENT_CHOICES = (
    (CONSENT_EMAIL, 'I would like to receive additional information by email'),
    (CONSENT_PHONE, ' I would like to receive additional information by telephone'),
)

USER_DATA_NAMES = {'ComparisonMarkets': 16384, 'UserProducts': 16384, 'UserMarkets': 16384, 'ActiveProduct': 256}

COUNTRY_FACTSHEET_CTA_TITLE = 'View latest trade statistics'

MENU_ITEM_ADD_CAMPAIGN_SITE_LINK = (
    'https://workspace.trade.gov.uk/working-at-dbt/how-do-i/editing-greatgovuk-campaign-sites-getting-started/'
)

PRODUCT_MARKET_DATA = {
    'algeria': {
        'display_name': 'Algeria',
        'card_link': 'https://www.great.gov.uk/markets/algeria/',
        'card_title': 'Exporting guide to Algeria',
        'card_content': (
            'Algeria is the largest country in Africa in terms of landmass and trade between the'
            + ' UK and Algeria is expanding. The economy is dominated by oil and gas production, '
            + 'but there is also a developing market in renewable energy production, such as wind and solar.'
        ),
    },
    'antigua and barbuda': {
        'display_name': 'Antigua and Barbuda',
        'card_link': 'https://www.great.gov.uk/markets/antigua-and-barbuda/',
        'card_title': 'Exporting guide to Antigua and Barbuda',
        'card_content': (
            'Antigua and Barbuda is a sovereign state in the West Indies consisting of a number of '
            + 'islands, with the two major ones being Antigua and Barbuda. The economy is heavily weighted '
            + 'toward tourism, but there are opportunities for exporters with the right goods and services'
        ),
    },
    'argentina': {
        'display_name': 'Argentina',
        'card_link': 'https://www.great.gov.uk/markets/argentina/',
        'card_title': 'Exporting guide to Argentina',
        'card_content': (
            'Argentina is the second largest economy in South America. It\'s a member of the G20 and the'
            + ' Mercosur trading block. Argentina has vast natural resources in agriculture, mining and '
            + 'energy including renewables. It has one of the highest English Proficiency Index scores in'
            + 'Latin America and its people have a European style business culture.'
        ),
    },
    'australia': {
        'display_name': 'Australia',
        'card_link': 'https://www.great.gov.uk/markets/australia/',
        'card_title': 'Exporting guide to Australia',
        'card_content': (
            'Australia shares a common language and culture with the UK, as well as free trade agreement. '
            + 'This makes it easier for UK companies to do business there.'
        ),
    },
    'austria': {
        'display_name': 'Austria',
        'card_link': 'https://www.great.gov.uk/markets/austria/',
        'card_title': 'Exporting guide to Austria',
        'card_content': (
            'Austria is situated in the heart of Europe. One of Europe’s wealthiest nations, Austria is a '
            + 'promising market for UK companies, especially for high quality products or services.'
        ),
    },
    'bahrain': {
        'display_name': 'Bahrain',
        'card_link': 'https://www.great.gov.uk/markets/bahrain/',
        'card_title': 'Exporting guide to Bahrain',
        'card_content': (
            'Bahrain is a small but prosperous economy, which has experienced steady growth. It has one '
            + 'of the most liberal business environments in the region.'
        ),
    },
    'barbados': {
        'display_name': 'Barbados',
        'card_link': 'https://www.great.gov.uk/markets/barbados/',
        'card_title': 'Exporting guide to Barbados',
        'card_content': (
            'Barbados is a popular tourist destination and the most eastern of all the Caribbean Islands. '
            + 'It is a developed country with a high quality of life and has had a long-standing trading '
            + 'relationship with UK.'
        ),
    },
    'belgium': {
        'display_name': 'Belgium',
        'card_link': 'https://www.great.gov.uk/markets/belgium/',
        'card_title': 'Exporting guide to Belgium',
        'card_content': (
            'Belgium is an affluent and multicultural country in the centre of Europe. It has a strong and '
            + 'longstanding trading relationship with the UK and is our eigth largest trading partner. '
            + 'English is an accepted business language and for many UK companies Belgium is just a short '
            + 'train ride away.'
        ),
    },
    'germany': {
        'display_name': 'Germany',
        'card_link': 'https://www.great.gov.uk/markets/germany/',
        'card_title': 'Exporting guide to Germany',
        'card_content': (
            'Germany is one of the world’s largest economies and a highly industrialised,'
            + 'diverse and stable market. It offers long-term potential and many opportunities'
            + ' for UK businesses offering innovative, quality products.'
        ),
    },
    'greece': {
        'display_name': 'Greece',
        'card_title': 'Exporting guide to Greece',
        'card_content': (
            'Situated in the Eastern Mediterranean, Greece is at the crossroads'
            + ' of three continents - Europe, Asia and Africa. The majority of the'
            + 'economy comprises of the services sector, with tourism playing a large part.'
        ),
    },
    'france': {'display_name': 'France', 'card_title': 'Exporting guide to France'},
}
