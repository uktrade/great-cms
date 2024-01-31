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
            "Argentina is the second largest economy in South America. It's a member of the G20 and the"
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
    'belize': {
        'display_name': 'Belize',
        'card_link': 'https://www.great.gov.uk/markets/belize/',
        'card_title': 'Exporting guide to Belize',
        'card_content': (
            'Located on the north eastern coast of Central America, Belize is bordered to the north west '
            + 'by Mexico, on the south and west by Guatemala, and to the east by the Caribbean Sea.'
        ),
    },
    'bosnia and herzegovina': {
        'display_name': 'Bosnia and Herzegovina',
        'card_link': 'https://www.great.gov.uk/markets/bosnia-and-herzegovina/',
        'card_title': 'Exporting guide to Bosnia and Herzegovina',
        'card_content': (
            'Situated at the heart of the Central and Eastern European (CEE) region, Bosnia and Herzegovina'
            + '(BiH) is showing firm and stable economic recovery, with increasing affluence creating '
            + 'opportunities for UK exporters. As an EU membership candidate (December 2022) it receives '
            + 'financial, administrative and technical support during its pre-accession period.'
        ),
    },
    'brazil': {
        'display_name': 'Brazil',
        'card_link': 'https://www.great.gov.uk/markets/brazil/',
        'card_title': 'Exporting guide to Brazil',
        'card_content': (
            'Brazil and the UK have long historical ties in trade and investment. The largest South '
            + 'American economy, Brazil has a familiar, European-style business culture.'
        ),
    },
    'brunei': {
        'display_name': 'Brunei',
        'card_link': 'https://www.great.gov.uk/markets/brunei/',
        'card_title': 'Exporting guide to Brunei',
        'card_content': (
            'Brunei is a politically stable country located on the island of Borneo. Oil and natural'
            + " gas account for a large part of the country's GDP and it is one of the largest producers "
            + 'of oil in South-East Asia.'
        ),
    },
    'bulgaria': {
        'display_name': 'Bulgaria',
        'card_link': 'https://www.great.gov.uk/markets/bulgaria/',
        'card_title': 'Exporting guide to Bulgaria',
        'card_content': (
            'Bulgaria is situated on the eastern side of the Balkans in South Eastern Europe. It is '
            + "part of the European single market and it's economy is broadly based on services, heavy"
            + 'industry and agriculture.'
        ),
    },
    'cambodia': {
        'display_name': 'Cambodia',
        'card_link': 'https://www.great.gov.uk/markets/cambodia/',
        'card_title': 'Exporting guide to Cambodia',
        'card_content': (
            'Cambodia is bordered by Vietnam, Laos and Thailand, with the Gulf of Thailand on its '
            + 'south-western coast. It has a population of over 16 million, with rising spending '
            + 'power predicted.'
        ),
    },
    'canada': {
        'display_name': 'Canada',
        'card_link': 'https://www.great.gov.uk/markets/canada/',
        'card_title': 'Exporting guide to Canada',
        'card_content': (
            'Canada is the second largest country in the world by area and has a population of over '
            + '37 million people. It’s politically stable with a strong record of economic growth and '
            + 'has well-established trade links with the UK.'
        ),
    },
    'chile': {
        'display_name': 'Chile',
        'card_link': 'https://www.great.gov.uk/markets/chile/',
        'card_title': 'Exporting guide to Chile',
        'card_content': (
            'Chile is one of the UK’s largest trading partners in Latin America and has enjoyed long '
            + 'periods of growth. A pro-business sentiment and a strong drive for innovative solutions '
            + 'make it a great first stop for companies new to the region.'
        ),
    },
    'china': {
        'display_name': 'China',
        'card_link': 'https://www.great.gov.uk/markets/china/',
        'card_title': 'Exporting guide to China',
        'card_content': (
            'China is the great economic success story of the last 30 years. It is a huge market for UK '
            + 'businesses in everything from technology to luxury food products.'
        ),
    },
    'colombia': {
        'display_name': 'Colombia',
        'card_link': 'https://www.great.gov.uk/markets/colombia/',
        'card_title': 'Exporting guide to Colombia',
        'card_content': (
            'After a long period of conflict, Colombia has emerged as a strong economy in its region. It '
            + 'has one of the largest populations and economies in Latin America and has seen recent '
            + 'improvements in the labour market.'
        ),
    },
    'costa rica': {
        'display_name': 'Costa Rica',
        'card_link': 'https://www.great.gov.uk/markets/costa-rica/',
        'card_title': 'Exporting guide to Costa Rica',
        'card_content': (
            'Costa Rica is a Central American country bordered by the Caribbean Sea to the north east and'
            + 'the Pacific Ocean to the south west.'
        ),
    },
    'croatia': {
        'display_name': 'Croatia',
        'card_link': 'https://www.great.gov.uk/markets/croatia/',
        'card_title': 'Exporting guide to Croatia',
        'card_content': (
            'Croatia occupies a strategic location at the heart of Central and Eastern Europe. Its economy'
            + 'is gaining strength and it offers a market with significant growth potential.'
        ),
    },
    'cyprus': {
        'display_name': 'Cyprus',
        'card_link': 'https://www.great.gov.uk/markets/cyprus/',
        'card_title': 'Exporting guide to Cyprus',
        'card_content': (
            'Cyprus is an island with a population of about one million people. Its strategic geographic '
            + 'location, at the corner of the eastern Mediterranean, between Europe, Asia and Africa, enhances'
            + 'its role as a regional business and trading hub. Cyprus enjoys close and strong links with UK at'
            + 'multiple levels. Overall, the Cyprus market is mature, competitive and price sensitive.'
        ),
    },
    'czech republic': {
        'display_name': 'Czech Republic',
        'card_link': 'https://www.great.gov.uk/markets/czech-republic/',
        'card_title': 'Exporting guide to Czech Republic',
        'card_content': (
            'The Czech Republic has a well developed and export-oriented economy. Its location in the centre '
            + 'of Europe gives UK exporters easy access to Germany and other Central and Eastern European (CEE)'
            + 'markets.'
        ),
    },
    'denmark': {
        'display_name': 'Denmark',
        'card_link': 'https://www.great.gov.uk/markets/denmark/',
        'card_title': 'Exporting guide to Denmark',
        'card_content': (
            'Denmark has a wealthy, educated and open economy, receptive to UK products and investments. The '
            + 'Danes are sophisticated buyers with a good reputation for paying suppliers on time.'
        ),
    },
    'dominica': {
        'display_name': 'Dominica',
        'card_link': 'https://www.great.gov.uk/markets/dominica/',
        'card_title': 'Exporting guide to Dominica',
        'card_content': (
            'Dominica is a small Caribbean country located between Guadeloupe and Martinique in the West '
            + 'Indies. Its economy is based around agriculture, tourism and investment.'
        ),
    },
    'dominican republic': {
        'display_name': 'Dominican Republic',
        'card_link': 'https://www.great.gov.uk/markets/dominican-republic/',
        'card_title': 'Exporting guide to Dominica',
        'card_content': (
            'The Dominican Republic has one of the largest and fastest growing economies in the Caribbean '
            + 'and Central American regions. Tourism, free trade zones and improved telecommunications are '
            + 'the main drivers of its growth.'
        ),
    },
    'Ecuador': {
        'display_name': 'Ecuador',
        'card_link': 'https://www.great.gov.uk/markets/ecuador/',
        'card_title': 'Exporting guide to Ecuador',
        'card_content': (
            "With a population of around 18 million, Ecuador is situated on South America's west coast. It "
            + 'is bordered by Colombia, Peru and the South Pacific Ocean.'
        ),
    },
    'Egypt': {
        'display_name': 'Egypt',
        'card_link': 'https://www.great.gov.uk/markets/egypt/',
        'card_title': 'Exporting guide to Egypt',
        'card_content': (
            'With its rapidly increasing population, advantageous geographic position and growing economy, '
            + 'Egypt is a market with a lot to offer. A number of UK companies are already doing business '
            + 'there, including BP, Shell, Vodafone, HSBC, GSK, AstraZeneca and Unilever.'
        ),
    },
    'el salvador': {
        'display_name': 'El Salvador',
        'card_link': 'https://www.great.gov.uk/markets/el-salvador/',
        'card_title': 'Exporting guide to El Salvador',
        'card_content': (
            'El Salvador, located between Honduras and Guatemala, is part of Central America. Despite being '
            + 'a small country, its population of over 6 million offers opportunities for UK exporters of '
            + 'goods and services.'
        ),
    },
    'estonia': {
        'display_name': 'Estonia',
        'card_link': 'https://www.great.gov.uk/markets/estonia/',
        'card_title': 'Exporting guide to Estonia',
        'card_content': (
            'Estonia is a Northern European hub for industrial, supply chain and global business services. '
            + 'It is an easy place to do and grow your business. For UK exporters who need local employees, '
            + 'Estonia has a hardworking, well-educated and skilled workforce. It is a world leader in '
            + "information technology producing 4 'unicorn' companies: Transferwise, Skype, Playtech and Taxify."
        ),
    },
    'faroe islands': {
        'display_name': 'Faroe Islands',
        'card_link': 'https://www.great.gov.uk/markets/faroe-islands/',
        'card_title': 'Exporting guide to Faroe Islands',
        'card_content': (
            'The Faroe Islands, located in the North Atlantic Ocean, comprise 18 islands. Fishing and related'
            + 'activities are the mains industries, but the Faroes are working towards a more diversified economy.'
        ),
    },
    'fiji': {
        'display_name': 'Fiji',
        'card_link': 'https://www.great.gov.uk/markets/fiji/',
        'card_title': 'Exporting guide to Fiji',
        'card_content': (
            'Fiji is a group of islands in the South Pacific Ocean, located near Australia and New Zealand. It '
            + 'has a population of just under 1 million and has one of the most developed economies in the Pacific'
            + 'islands.'
        ),
    },
    'finland': {
        'display_name': 'Finland',
        'card_link': 'https://www.great.gov.uk/markets/finland/',
        'card_title': 'Exporting guide to Finland',
        'card_content': (
            'Finland has an affluent, highly educated and technologically sophisticated population. British '
            + 'quality products are well received and UK brands are well known in the country.'
        ),
    },
    'france': {
        'display_name': 'France',
        'card_link': 'https://www.great.gov.uk/markets/france/',
        'card_title': 'Exporting guide to France',
        'card_content': (
            "France is one of the UK's largest export markets and a major global economy. In easy reach of "
            + 'the UK, it offers many export opportunities for businesses offering innovative, quality products.'
        ),
    },
    'germany': {
        'display_name': 'Germany',
        'card_link': 'https://www.great.gov.uk/markets/germany/',
        'card_title': 'Exporting guide to Germany',
        'card_content': (
            'Germany is one of the world’s largest economies and a highly industrialised, diverse and stable '
            + 'market. It offers long-term potential and many opportunities for UK businesses offering '
            + 'innovative, quality products.'
        ),
    },
    'ghana': {
        'display_name': 'Ghana',
        'card_link': 'https://www.great.gov.uk/markets/ghana/',
        'card_title': 'Exporting guide to Ghana',
        'card_content': (
            'The UK and Ghana share a common business language, the same time zone for half '
            + 'the year and good flight connections.'
        ),
    },
    'greece': {
        'display_name': 'Greece',
        'card_link': 'https://www.great.gov.uk/markets/greece/',
        'card_title': 'Exporting guide to Greece',
        'card_content': (
            'Situated in the Eastern Mediterranean, Greece is at the crossroads'
            + ' of three continents - Europe, Asia and Africa. The majority of the'
            + 'economy comprises of the services sector, with tourism playing a large part.'
        ),
    },
    'grenada': {
        'display_name': 'Grenada',
        'card_link': 'https://www.great.gov.uk/markets/grenada/',
        'card_title': 'Exporting guide to Grenada',
        'card_content': (
            'Grenada is an island in the West Indies at the southern end of the Grenadines'
            + ' island chain. As a commonwealth country it has strong ties to the UK. '
            + "Tourism and agriculture are the mainstays of it's economy"
        ),
    },
    'guatemala': {
        'display_name': 'Guatemala',
        'card_link': 'https://www.great.gov.uk/markets/guatemala/',
        'card_title': 'Exporting guide to Guatemala',
        'card_content': (
            'Guatemala is in Central America and has the largest economy in the region. '
            + 'Bordered by Mexico, Honduras, El Salvador and Belize, it has good access '
            + 'to North and Central America.'
        ),
    },
    'guyana': {
        'display_name': 'Guyana',
        'card_link': 'https://www.great.gov.uk/markets/guyana/',
        'card_title': 'Exporting guide to Guyana',
        'card_content': (
            'Guatemala is in Central America and has the largest economy in the region. '
            + 'Bordered by Mexico, Honduras, El Salvador and Belize, it has good access '
            + 'to North and Central America.'
        ),
    },
}
