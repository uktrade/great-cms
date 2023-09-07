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

GET_EXPORT_HELP_CHOICE_TO_CONTENT_MAPPING = {
    'finding_an_overseas_buyer': {
        'title': 'Find an overseas buyer',
        'links': [
            {'text': 'Find an export opportunity', 'link': 'https://www.great.gov.uk/export-opportunities'},
            {
                'text': 'Ask the export support team a question',
                'link': 'https://www.gov.uk/ask-export-support-team',
            },
        ],
    },
    'choosing_a_market': {
        'title': 'Choose a market',
        'links': [
            {'text': 'Research a market', 'link': 'https://www.great.gov.uk/markets/'},
            {'text': 'Find an export market', 'link': 'https://www.great.gov.uk/advice/find-an-export-market/'},
        ],
    },
    'cost_of_exporting': {
        'title': 'Cost of Exporting',
        'links': [
            {'text': 'Create an export plan', 'link': 'https://www.great.gov.uk/export-plan/'},
            {
                'text': 'Understand business risks when exporting',
                'link': 'https://www.great.gov.uk/advice/prepare-to-do-business-in-a-foreign-country/understand-business-risks-when-exporting/',  # noqa: E501
            },
            {
                'text': 'Get export finance',
                'link': 'https://www.great.gov.uk/advice/get-export-finance-and-funding/',
            },
        ],
    },
    'duties_and_taxes': {
        'title': 'Duties & Taxes',
        'links': [
            {
                'text': 'Understand duties and taxes',
                'link': 'https://www.great.gov.uk/learn/categories/selling-across-borders-product-and-services-regulations-licensing-and-logistics/get-your-goods-into-the-destination-country/understand-duties-and-taxes/',  # noqa: E501
            }
        ],
    },
    'how_to_start_exporting_today': {
        'title': 'How to start exporting today',
        'links': [
            {'text': 'Learn to export', 'link': 'https://www.great.gov.uk/learn/categories/'},
        ],
    },
    'other': {
        'title': '',
        'links': [
            {'text': 'Choose a route to market', 'link': 'https://www.great.gov.uk/advice/define-route-to-market/'},
            {'text': 'Sell services overseas', 'link': 'https://www.great.gov.uk/advice/sell-services-overseas/'},
        ],
    },
    'not_sure': {
        'title': '',
        'links': [
            {'text': 'Export Academy', 'link': 'https://www.great.gov.uk/export-academy/'},
        ],
    },
}
