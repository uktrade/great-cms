from enum import Enum

from django.conf import settings

SERVICE_NAME = 'great-cms'

VIDEO_DURATION_DATA_ATTR_NAME = 'data-v-duration'

BACKLINK_QUERYSTRING_NAME = 'return-link'

# Wagtails default features to allow for easy adding of additional features
RICHTEXT_FEATURES__DEFAULT = [
    'bold',
    'italic',
    'h2',
    'h3',
    'h4',
    'ol',
    'ul',
    'hr',
    'anchor-identifier',
    'embed',
    'link',
    'document-link',
    'image',
]

RICHTEXT_FEATURES__DEFAULT__ALLOW_SUPERSCRIPT = RICHTEXT_FEATURES__DEFAULT + ['superscript']

# Define a strict subset of rich-text features only includes linebreaks
RICHTEXT_FEATURES__MINIMAL = ()

RICHTEXT_FEATURES__WITH_LIST = ['ol', 'ul']
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
            + ' Latin America and its people have a European style business culture.'
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
            'Situated at the heart of the Central and Eastern European (CEE) region, Bosnia and Herzegovina '
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
            + "part of the European single market and it's economy is broadly based on services, heavy "
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
            + ' the Pacific Ocean to the south west.'
        ),
    },
    'croatia': {
        'display_name': 'Croatia',
        'card_link': 'https://www.great.gov.uk/markets/croatia/',
        'card_title': 'Exporting guide to Croatia',
        'card_content': (
            'Croatia occupies a strategic location at the heart of Central and Eastern Europe. Its economy'
            + ' is gaining strength and it offers a market with significant growth potential.'
        ),
    },
    'cyprus': {
        'display_name': 'Cyprus',
        'card_link': 'https://www.great.gov.uk/markets/cyprus/',
        'card_title': 'Exporting guide to Cyprus',
        'card_content': (
            'Cyprus is an island with a population of about one million people. Its strategic geographic '
            + 'location, at the corner of the eastern Mediterranean, between Europe, Asia and Africa, enhances'
            + ' its role as a regional business and trading hub. Cyprus enjoys close and strong links with UK at'
            + ' multiple levels. Overall, the Cyprus market is mature, competitive and price sensitive.'
        ),
    },
    'czech republic': {
        'display_name': 'Czech Republic',
        'card_link': 'https://www.great.gov.uk/markets/czech-republic/',
        'card_title': 'Exporting guide to Czech Republic',
        'card_content': (
            'The Czech Republic has a well developed and export-oriented economy. Its location in the centre '
            + 'of Europe gives UK exporters easy access to Germany and other Central and Eastern European (CEE)'
            + ' markets.'
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
    'ecuador': {
        'display_name': 'Ecuador',
        'card_link': 'https://www.great.gov.uk/markets/ecuador/',
        'card_title': 'Exporting guide to Ecuador',
        'card_content': (
            "With a population of around 18 million, Ecuador is situated on South America's west coast. It "
            + 'is bordered by Colombia, Peru and the South Pacific Ocean.'
        ),
    },
    'egypt': {
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
            'The Faroe Islands, located in the North Atlantic Ocean, comprise 18 islands. Fishing and related '
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
            + ' islands.'
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
            + ' of three continents - Europe, Asia and Africa. The majority of the '
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
            'Guyana borders Brazil and Venezuela in the north of South America '
            + 'and is the only English-speaking nation on the continent.'
        ),
    },
    'honduras': {
        'display_name': 'Honduras',
        'card_link': 'https://www.great.gov.uk/markets/honduras/',
        'card_title': 'Exporting guide to Honduras',
        'card_content': (
            'Honduras is a Central American country bordered by Guatemala, El Salvador and'
            + " Nicaragua. It's economy is primarily based around agriculture."
        ),
    },
    'hong kong, china': {
        'display_name': 'Hong Kong, China',
        'card_link': 'https://www.great.gov.uk/markets/hong-kong-china/',
        'card_title': 'Exporting guide to Hong Kong, China',
        'card_content': (
            'As one of Asia’s leading financial and business centres, Hong Kong has an open, '
            + 'transparent and competitive market. English is widely spoken. It has '
            + 'sophisticated financial services and distribution links, an efficient port '
            + 'terminal, a free port status and unrivalled connectivity to mainland China '
            + 'through air, rail, road and sea.'
        ),
    },
    'hungary': {
        'display_name': 'Hungary',
        'card_link': 'https://www.great.gov.uk/markets/hungary/',
        'card_title': 'Exporting guide to Hungary',
        'card_content': (
            'Hungary is a high-growth business hub in the heart of Europe. It has a population '
            + 'of almost 10 million and a motivated workforce. As well as a favourable '
            + 'geographical location, Hungary offers a modern, liberalised business environment '
            + 'with a strong legal system.'
        ),
    },
    'iceland': {
        'display_name': 'Iceland',
        'card_link': 'https://www.great.gov.uk/markets/iceland/',
        'card_title': 'Exporting guide to Iceland',
        'card_content': (
            'An island country in the North Atlantic Iceland is about 840 km north-west of the UK'
            + " and about 460 km south-east of Greenland's coast. Although it is one of the least "
            + 'densely populated countries in Europe, it has a strong import market where UK goods '
            + 'and services are popular.'
        ),
    },
    'india': {
        'display_name': 'India',
        'card_link': 'https://www.great.gov.uk/markets/india/',
        'card_title': 'Exporting guide to India',
        'card_content': (
            'The size of India’s economy makes it an attractive market for UK exporters. India has'
            + ' a range of exciting export opportunities across a large number of sectors, although '
            + 'success in this market can require patience and a longer-term approach.'
        ),
    },
    'indonesia': {
        'display_name': 'Indonesia',
        'card_link': 'https://www.great.gov.uk/markets/indonesia/',
        'card_title': 'Exporting guide to Indonesia',
        'card_content': (
            'Indonesia is a group of islands located near Malaysia, Singapore, the Philippines and '
            + 'Australia. The country has a population of over 270 million, making it a large '
            + 'potential consumer base.'
        ),
    },
    'ireland': {
        'display_name': 'Ireland',
        'card_link': 'https://www.great.gov.uk/markets/ireland/',
        'card_title': 'Exporting guide to Ireland',
        'card_content': (
            'Ireland is an important trading partner for the UK. Trade and foreign investment is '
            + "encouraged and growth is strong. Ireland's similarities to the UK make it an ideal "
            + 'market for first-time exporters.'
        ),
    },
    'israel': {
        'display_name': 'Israel',
        'card_link': 'https://www.great.gov.uk/markets/israel/',
        'card_title': 'Exporting guide to Israel',
        'card_content': (
            'Israel is a highly developed, western-orientated market whose business practice is '
            + 'similar to much of Western Europe. UK exports to Israel have grown steadily and '
            + 'many British companies have a major presence in the market.'
        ),
    },
    'italy': {
        'display_name': 'Italy',
        'card_link': 'https://www.great.gov.uk/markets/italy/',
        'card_title': 'Exporting guide to Italy',
        'card_content': (
            'Italy is one of the UK’s closest trading partners and biggest export markets, and '
            + 'presents significant opportunities for UK businesses. There is demand for defence, '
            + 'cyber security, aerospace and engineering skills. Trade with the city of Milan and '
            + 'the surrounding region is especially strong.'
        ),
    },
    'ivory coast': {
        'display_name': 'Ivory Coast',
        'card_link': 'https://www.great.gov.uk/markets/ivory-coast/',
        'card_title': 'Exporting guide to Ivory Coast',
        'card_content': (
            'The Ivory Coast (also known as The Republic of Côte D’Ivoire) is one of the largest '
            + 'economies of the Economic Community of West Africa States (ECOWAS). It is a growing '
            + 'regional hub and can be the gateway to French-speaking Africa and the rest of the '
            + 'region for exporters.'
        ),
    },
    'jamaica': {
        'display_name': 'Jamaica',
        'card_link': 'https://www.great.gov.uk/markets/jamaica/',
        'card_title': 'Exporting guide to Jamaica',
        'card_content': (
            'Jamaica is an island country in the Caribbean Sea. Its strategic location gives direct '
            + 'sea and air freight links to the UK and the wider Caribbean.'
        ),
    },
    'japan': {
        'display_name': 'Japan',
        'card_link': 'https://www.great.gov.uk/markets/japan/',
        'card_title': 'Exporting guide to Japan',
        'card_content': (
            'Japan is currently the third largest economy in the world. With our new free trade '
            + 'agreement, we have entered an exciting new chapter in trading relations between '
            + 'the UK and Japan.'
        ),
    },
    'jordan': {
        'display_name': 'Jordan',
        'card_link': 'https://www.great.gov.uk/markets/jordan/',
        'card_title': 'Exporting guide to Jordan',
        'card_content': (
            'In recent years, Jordan has undertaken economic reform and re-opened borders with '
            + 'neighbouring markets. This has created new opportunities in this market for UK '
            + 'businesses.'
        ),
    },
    'kenya': {
        'display_name': 'Kenya',
        'card_link': 'https://www.great.gov.uk/markets/kenya/',
        'card_title': 'Exporting guide to Kenya',
        'card_content': (
            'Kenya is a relatively mature market economy and a regional financial hub, with '
            + 'strong links to the UK. It boasts a well-educated, English-speaking and '
            + 'productive labour force. UK firms say staff retention rates are high. It’s '
            + 'an increasingly open, competitive and easy place to do business.'
        ),
    },
    'latvia': {
        'display_name': 'Latvia',
        'card_link': 'https://www.great.gov.uk/markets/latvia/',
        'card_title': 'Exporting guide to Latvia',
        'card_content': (
            'In Latvia rapid economic growth has been driven mainly by an increase in '
            + 'investment and private consumption. High-quality British products are well '
            + 'received and the UK brand is immediately recognised. It’s an ideal starter '
            + 'market for UK companies new to exporting.'
        ),
    },
    'lebanon': {
        'display_name': 'Lebanon',
        'card_link': 'https://www.great.gov.uk/markets/lebanon/',
        'card_title': 'Exporting guide to Lebanon',
        'card_content': (
            'Despite political and economic challenges, Lebanese businesses are adept at '
            + 'staying afloat throughout any turmoil. The private sector in Lebanon has '
            + 'always found a way to survive, even with little government support and a '
            + 'lack of some basic infrastructure.'
        ),
    },
    'liechtenstein': {
        'display_name': 'Liechtenstein',
        'card_link': 'https://www.great.gov.uk/markets/liechtenstein/',
        'card_title': 'Exporting guide to Liechtenstein',
        'card_content': (
            'Liechtenstein is a relatively small but buoyant market for UK exporters. A '
            + 'free trade agreement (FTA) between the UK and Liechtenstein, along with '
            + 'Norway and Iceland, is now in effect. The FTA recognises the importance of'
            + ' SMEs and contains commitments to co-operate on SME trade and investment '
            + 'opportunities.'
        ),
    },
    'lithuania': {
        'display_name': 'Lithuania',
        'card_link': 'https://www.great.gov.uk/markets/lithuania/',
        'card_title': 'Exporting guide to Lithuania',
        'card_content': (
            'Located at a crossroads between Northern, Central and Eastern Europe, '
            + 'Lithuania is politically stable. Its economy is small but diverse, with '
            + 'established manufacturing and agricultural sectors and growing technology '
            + 'and service sectors.'
        ),
    },
    'luxembourg': {
        'display_name': 'Luxembourg',
        'card_link': 'https://www.great.gov.uk/markets/luxembourg/',
        'card_title': 'Exporting guide to Luxembourg',
        'card_content': (
            'Luxembourg is located in Western Europe and has a population of over 600,000 '
            + 'people. It is landlocked, and bordered by Belgium, France and Germany. '
            + 'Despite the relatively small size of the country, the UK has previously '
            + 'exported large amounts goods and services to Luxembourg.'
        ),
    },
    'madagascar': {
        'display_name': 'Madagascar',
        'card_link': 'https://www.great.gov.uk/markets/madagascar/',
        'card_title': 'Exporting guide to Madagascar',
        'card_content': (
            'Madagascar is an island located off the East African coast, close to Mozambique,'
            + ' Reunion and Mauritius. The economy mainly revolves around tourism, textiles, '
            + 'agriculture and mining.'
        ),
    },
    'malaysia': {
        'display_name': 'Malaysia',
        'card_link': 'https://www.great.gov.uk/markets/malaysia/',
        'card_title': 'Exporting guide to Malaysia',
        'card_content': (
            'Decades of growth and stability have helped make Malaysia an industrialised, '
            + 'relatively open economy with consistent growth. Despite the impact of the '
            + 'Covid-19 pandemic, Malaysia continues to offers opportunities across a wide '
            + 'range of sectors for UK exporters as demand picks up for a variety of goods '
            + 'and services.'
        ),
    },
    'malta': {
        'display_name': 'Malta',
        'card_link': 'https://www.great.gov.uk/markets/malta/',
        'card_title': 'Exporting guide to Malta',
        'card_content': (
            'Malta is an island located off the south coast of Italy. It has weathered the '
            + 'economic crises of the last few years well, leaving it with a strong and '
            + 'vibrant economy.'
        ),
    },
    'mauritius': {
        'display_name': 'Mauritius',
        'card_link': 'https://www.great.gov.uk/markets/mauritius/',
        'card_title': 'Exporting guide to Mauritius',
        'card_content': (
            "Mauritius' economy has gradually moved away from being sugar-based by "
            + 'diversifying into other industries. Mauritius has successfully positioned '
            + 'itself as a regional business and trade hub due to its strategic, geographic '
            + 'location and impressive economic development.'
        ),
    },
    'mexico': {
        'display_name': 'Mexico',
        'card_link': 'https://www.great.gov.uk/markets/mexico/',
        'card_title': 'Exporting guide to Mexico',
        'card_content': (
            'Mexico is a North American country south of the United States. The World Bank '
            + 'now classes Mexico as an upper-middle-income country and the economically '
            + 'active population continues to grow.'
        ),
    },
    'mongolia': {
        'display_name': 'Mongolia',
        'card_link': 'https://www.great.gov.uk/markets/mongolia/',
        'card_title': 'Exporting guide to Mongolia',
        'card_content': (
            'Mongolia, situated in east and central Asia, is more than 6 times the size of '
            + 'the UK. Mining is a large economic sector for Mongolia, and the renewable '
            + 'energy sector is also expanding. The overall business environment is improving.'
        ),
    },
    'morocco': {
        'display_name': 'Morocco',
        'card_link': 'https://www.great.gov.uk/markets/morocco/',
        'card_title': 'Exporting guide to Morocco',
        'card_content': (
            'Morocco is a politically stable, business-friendly country. Though its economy has '
            + 'traditionally been more aligned to Europe than to Africa, Morocco is increasingly '
            + 'taking advantage of opportunities across the African continent. This opening up of '
            + 'the Moroccan economy is creating further opportunities for UK firms.'
        ),
    },
    'mozambique': {
        'display_name': 'Mozambique',
        'card_link': 'https://www.great.gov.uk/markets/mozambique/',
        'card_title': 'Exporting guide to Mozambique',
        'card_content': (
            'Mozambique has a population of over 30 million inhabitants and a wealth of natural '
            + "resources. It's long southeast African coastline makes it ideally placed for "
            + 'trade with Europe and Asia.'
        ),
    },
    'new zealand': {
        'display_name': 'New Zealand',
        'card_link': 'https://www.great.gov.uk/markets/new-zealand/',
        'card_title': 'Exporting guide to New Zealand',
        'card_content': (
            'UK-New Zealand bilateral trade continues to increase and is set to grow further '
            + 'under the new UK-New Zealand free trade agreement.'
        ),
    },
    'nicaragua': {
        'display_name': 'Nicaragua',
        'card_link': 'https://www.great.gov.uk/markets/nicaragua/',
        'card_title': 'Exporting guide to Nicaragua',
        'card_content': (
            'Nicaragua is the largest country in Central America. Its sustained economic growth '
            + 'and qualified labour force attracts foreign investment. Nicaragua’s main industries'
            + ' include agriculture and tourism.'
        ),
    },
    'nigeria': {
        'display_name': 'Nigeria',
        'card_link': 'https://www.great.gov.uk/markets/nigeria/',
        'card_title': 'Exporting guide to Nigeria',
        'card_content': (
            'Nigeria has the largest population and economy in Africa. English is the most widely '
            + 'spoken language and Nigeria has similar business and legal practices to the UK.'
        ),
    },
    'norway': {
        'display_name': 'Norway',
        'card_link': 'https://www.great.gov.uk/markets/norway/',
        'card_title': 'Exporting guide to Norway',
        'card_content': (
            'Norway is part of the Nordic and Baltic region and is the fourth largest country in '
            + 'Europe. It is a sophisticated and established market, having a long and trusted '
            + 'trading relationship with the UK.'
        ),
    },
    'oman': {
        'display_name': 'Oman',
        'card_link': 'https://www.great.gov.uk/markets/oman/',
        'card_title': 'Exporting guide to Oman',
        'card_content': (
            'The Sultanate of Oman is the second largest country geographically in the Gulf '
            + 'Cooperation Council (GCC). Its strategic location within the Arabian Peninsula, '
            + 'internal political stability, a favourable tax regime and strong existing links '
            + 'with the UK offer significant export opportunities for UK businesses.'
        ),
    },
    'panama': {
        'display_name': 'Panama',
        'card_link': 'https://www.great.gov.uk/markets/panama/',
        'card_title': 'Exporting guide to Panama',
        'card_content': (
            'Panama offers regional as well as bilateral opportunities for UK companies. Its '
            + 'strategic geographical location, dollarised economy, and social, political and '
            + 'economic stability make Panama an excellent base from which to do business in '
            + "the region. Panama's government actively promotes policies to attract foreign "
            + 'companies and stimulate innovation, through the creation of a series of Special '
            + 'Economic Zones (SEZs).'
        ),
    },
    'papua new guinea': {
        'display_name': 'Papua New Guinea',
        'card_link': 'https://www.great.gov.uk/markets/papua-new-guinea/',
        'card_title': 'Exporting guide to Papua New Guinea',
        'card_content': (
            'Papua New Guinea (PNG) is in the southwestern Pacific and includes the eastern '
            + 'half of New Guinea and its offshore islands. The PNG mainland has around 600 '
            + 'islands with a total land area of 452,860 square kilometers. Over 800 languages '
            + 'are spoken. It has a population of approximately 8.4 million giving UK companies '
            + 'access to a good consumer market. Papua New Guinea is largely underdeveloped. It '
            + 'is dominated by the agricultural, forestry, and fishing sector and the minerals '
            + 'and energy extraction sector.'
        ),
    },
    'paraguay': {
        'display_name': 'Paraguay',
        'card_link': 'https://www.great.gov.uk/markets/paraguay/',
        'card_title': 'Exporting guide to Paraguay',
        'card_content': (
            'A South American country with a population of over 7 million people, Paraguay has '
            + 'an abundance of natural resources and renewable energy. It is landlocked and '
            + 'bordered by Argentina, Brazil and Bolivia. It has a growing import market and '
            + 'UK companies looking to export to Paraguay may benefit from the increase in '
            + 'demand for UK goods and services.'
        ),
    },
    'peru': {
        'display_name': 'Peru',
        'card_link': 'https://www.great.gov.uk/markets/peru/',
        'card_title': 'Exporting guide to Peru',
        'card_content': (
            'Peru has been the fastest growing economy in Latin America for most of the past '
            + 'decade. Key export sectors for the UK include health and life sciences, mining, '
            + 'energy, sustainable infrastructure, and security. The UK and Peru have a close '
            + 'and constructive trade and investment relationship.'
        ),
    },
    'philippines': {
        'display_name': 'Philippines',
        'card_link': 'https://www.great.gov.uk/markets/philippines/',
        'card_title': 'Exporting guide to Philippines',
        'card_content': (
            'The Philippines is an archipelago composed of about 7,640 islands and a population'
            + ' of 109 million people. It provides a vast market for UK companies and offers many'
            + ' opportunities for companies to export their goods and services. '
            + 'UK business, telecoms and financial services all have a strong presence in the '
            + 'Philippines and are well recognised.'
        ),
    },
    'poland': {
        'display_name': 'Poland',
        'card_link': 'https://www.great.gov.uk/markets/poland/',
        'card_title': 'Exporting guide to Poland',
        'card_content': (
            'Located in Central Europe, Poland is divided into 16 administrative provinces called'
            + ' voivodeships, covering an area of 312,696 km2. It has a strong growing economy, '
            + 'and the spending power of Polish consumers increase the benefit of UK exporters.'
        ),
    },
    'portugal': {
        'display_name': 'Portugal',
        'card_link': 'https://www.great.gov.uk/markets/portugal/',
        'card_title': 'Exporting guide to Portugal',
        'card_content': (
            'Located on the western edge of the Iberian peninsula, '
            + 'Portugal is a good market for UK exporters. Anchored by the world’s oldest bilateral alliance'
            + ' trade links are strong, particularly within the tourism industry and expat communities.'
        ),
    },
    'qatar': {
        'display_name': 'Qatar',
        'card_link': 'https://www.great.gov.uk/markets/qatar/',
        'card_title': 'Exporting guide to Qatar',
        'card_content': (
            'Qatar has one of the highest levels of GDP per capita in the world, making it an affluent market'
            + '. Qatar is a key market both for trade and investment because of its dynamic and'
            + ' diversifying economy, and the wide variety of growth areas identified in its National Vision.'
        ),
    },
    'romania': {
        'display_name': 'Romania',
        'card_link': 'https://www.great.gov.uk/markets/romania/',
        'card_title': 'Exporting guide to Romania',
        'card_content': (
            'Romania is located in South East Europe at the strategic crossroads of the European Union (EU), '
            + 'the Commonwealth of Independent States (CIS) and the Middle East. It is part of the Central and'
            + ' Eastern European (CEE) region, which offers considerable potential for British businesses. '
            + 'The CEE region is easily accessible from the UK and offers a market of over 100 million consumers. '
            + 'There is a widespread use of English as the business language '
            + 'and the country acts as a gateway into the other CEE markets.'
        ),
    },
    'saudi arabia': {
        'display_name': 'Saudi Arabia',
        'card_link': 'https://www.great.gov.uk/markets/saudi-arabia/',
        'card_title': 'Exporting guide to Saudi Arabia',
        'card_content': (
            'The Kingdom of Saudi Arabia is a high-income country. It has a large population, '
            + 'significant purchasing power and a growing reputation as an important destination for many'
            + ' foreign brands and companies in many different sectors.'
        ),
    },
    'serbia': {
        'display_name': 'Serbia',
        'card_link': 'https://www.great.gov.uk/markets/serbia/',
        'card_title': 'Exporting guide to Serbia',
        'card_content': (
            'Serbia is a landlocked country at the crossroads of'
            + ' Central and Southeast Europe, with a population close to 7 million people.'
        ),
    },
    'seychelles': {
        'display_name': 'Seychelles',
        'card_link': 'https://www.great.gov.uk/markets/seychelles/',
        'card_title': 'Exporting guide to Seychelles',
        'card_content': (
            'Seychelles is a chain of islands off the west coast of Africa'
            + ', with a population of just under 100,000 people. '
            + ' Tourism is the main industry on the islands.'
        ),
    },
    'singapore': {
        'display_name': 'Singapore',
        'card_link': 'https://www.great.gov.uk/markets/singapore/',
        'card_title': 'Exporting guide to Singapore',
        'card_content': (
            'Singapore is a small, but wealthy city-state with an open and trade-driven economy. '
            + 'It is a leading financial, shipping, and trade hub for the Asia Pacific region, '
            + 'and the government has a pro-business economic and trade policy.'
        ),
    },
    'slovakia': {
        'display_name': 'Slovakia',
        'card_link': 'https://www.great.gov.uk/markets/slovakia/',
        'card_title': 'Exporting guide to Slovakia',
        'card_content': (
            'Slovakia combines a stable economic and political environment with a strategic '
            + 'geographical location. English is widely spoken as a business '
            + 'language, and several large UK companies operate in Slovakia.'
        ),
    },
    'slovenia': {
        'display_name': 'Slovenia',
        'card_link': 'https://www.great.gov.uk/markets/slovenia/',
        'card_title': 'Exporting guide to Slovenia',
        'card_content': (
            'Slovenia is one of a group of 9 emerging markets in Central and Eastern Europe (CEE). '
            + "It's one of the most developed markets in the region and there are long-term growth "
            + 'prospects for UK companies.'
        ),
    },
    'south africa': {
        'display_name': 'South Africa',
        'card_link': 'https://www.great.gov.uk/markets/south-africa/',
        'card_title': 'Exporting guide to South Africa',
        'card_content': (
            'South Africa, located at the bottom of the African continent and filled with natural resources, '
            + 'is a sophisticated and promising market. It has a well developed economic infrastructure '
            + 'and opportunities in its emerging markets.'
        ),
    },
    'south korea': {
        'display_name': 'South Korea',
        'card_link': 'https://www.great.gov.uk/markets/south-korea/',
        'card_title': 'Exporting guide to South Korea',
        'card_content': (
            'South Korea is one of the largest economies in the world and has strong trade links with the UK. '
            + 'The UK has a Continuity Free Trade Agreement in place with South Korea which came into effect '
            + 'in January 2020.'
        ),
    },
    'spain': {
        'display_name': 'Spain',
        'card_link': 'https://www.great.gov.uk/markets/spain/',
        'card_title': 'Exporting guide to Spain',
        'card_content': (
            'Spain is located in Southwestern Europe and borders France and Portugal. It is one '
            + 'of the biggest consumer markets in the EU and with a population of 46.4 million '
            + 'it provides a large consumer base for UK exporters to sell to. Spain is one of '
            + 'the top 10 largest trading partners of the UK. There is a demand for UK goods '
            + 'and services which UK businesses looking to export could benefit from.'
        ),
    },
    'st kitts and nevis': {
        'display_name': 'St Kitts and Nevis',
        'card_link': 'https://www.great.gov.uk/markets/st-kitts-and-nevis/',
        'card_title': 'Exporting guide to St Kitts and Nevis',
        'card_content': (
            'St Kitts and Nevis is part of the Lesser Antilles island chain in the Caribbean, '
            + 'close to Anguilla, Antigua and Barbuda and Monserrat. '
            + 'It is part of the Commonwealth and one of the smallest countries in the world.'
        ),
    },
    'st lucia': {
        'display_name': 'St Lucia',
        'card_link': 'https://www.great.gov.uk/markets/st-lucia/',
        'card_title': 'Exporting guide to St Lucia',
        'card_content': (
            'Saint Lucia is an Eastern Caribbean island nation with a population of 183,000 people. '
            + 'The service sector makes up a large part of its economy, including tourism and financial '
            + 'services.'
        ),
    },
    'st vincent and the grenadines': {
        'display_name': 'St Vincent and the Grenadines',
        'card_link': 'https://www.great.gov.uk/markets/st-vincent-and-grenadines/',
        'card_title': 'Exporting guide to St Vincent and the Grenadines',
        'card_content': (
            'St Vincent and the Grenadines is a southern Caribbean nation '
            + 'comprising of the main island of St. Vincent, and a chain of smaller islands. '
            + 'Its main industries are agriculture and tourism.'
        ),
    },
    'suriname': {
        'display_name': 'Suriname',
        'card_link': 'https://www.great.gov.uk/markets/suriname/',
        'card_title': 'Exporting guide to Suriname',
        'card_content': (
            'Suriname is the smallest country in South America. It borders Guyana, French Guiana '
            + 'and Brazil, '
            + 'making it a good gateway into the South American market. It is a member of the '
            + 'Caribbean Community (CARICOM). '
            + 'The current climate in Suriname, supports and promotes foreign direct investment '
            + '(FDI), which has helped contribute to its economy.'
        ),
    },
    'sweden': {
        'display_name': 'Sweden',
        'card_link': 'https://www.great.gov.uk/markets/sweden/',
        'card_title': 'Exporting guide to Sweden',
        'card_content': (
            'Sweden is among the most competitive, innovative and globalised nations '
            + 'in the world. The country has a stable economy, a skilled labour force '
            + 'and sophisticated consumers.'
        ),
    },
    'switzerland': {
        'display_name': 'Switzerland',
        'card_link': 'https://www.great.gov.uk/markets/switzerland/',
        'card_title': 'Exporting guide to Switzerland',
        'card_content': (
            'An innovative country at the heart of Europe, Switzerland has a stable and reliable business'
            + ', legal and regulatory environment. It is one of the UK’s closest trading partners. '
            + 'British companies of all sizes '
            + 'are trading there, and UK investment is particularly substantial in the services and '
            + 'manufacturing sectors.'
        ),
    },
    'taiwan': {
        'display_name': 'Taiwan',
        'card_link': 'https://www.great.gov.uk/markets/taiwan/',
        'card_title': 'Exporting guide to Taiwan',
        'card_content': (
            'Taiwan is an advanced, high-tech economy with a strategic location'
            + ' in the Asia Pacific region. It has modern infrastructure and its banking, '
            + 'insurance and securities sectors are being liberalised.'
        ),
    },
    'tanzania': {
        'display_name': 'Tanzania',
        'card_link': 'https://www.great.gov.uk/markets/tanzania/',
        'card_title': 'Exporting guide to Tanzania',
        'card_content': (
            'Tanzania is located on the East Coast of Africa. Due to its borders with Kenya, Uganda, '
            + 'Rwanda, Burundi, the Democratic Republic of Congo, Zambia, Malawi and Mozambique,'
            + ' it can be a good gateway to these landlocked countries.'
        ),
    },
    'thailand': {
        'display_name': 'Thailand',
        'card_link': 'https://www.great.gov.uk/markets/thailand/',
        'card_title': 'Exporting guide to Thailand',
        'card_content': (
            'As the second largest economy in Southeast Asia, Thailand has a strong consumer base with large'
            + ', urban, middle-class population. With its well-established trade relationship with the '
            + 'UK, cultural goodwill '
            + 'and central location, Thailand is a promising export market for British businesses.'
        ),
    },
    'the bahamas': {
        'display_name': 'The Bahamas',
        'card_link': 'https://www.great.gov.uk/markets/bahamas/',
        'card_title': 'Exporting guide to The Bahamas',
        'card_content': (
            'The Bahamas is located within the Lucayan Archipelago in the West Indies,'
            + ' and is near Florida, Cuba, the Dominican Republic and Turks '
            + 'and Caicos, which is also part of the Lucayan Archipelago.'
        ),
    },
    'the netherlands': {
        'display_name': 'The Netherlands',
        'card_link': 'https://www.great.gov.uk/markets/netherlands/',
        'card_title': 'Exporting guide to The Netherlands',
        'card_content': (
            'The Netherlands has a thriving economy and is a major gateway to Europe.'
            + ' It is culturally similar to the UK, making it an ideal test market for products.'
        ),
    },
    'trinidad and tobago': {
        'display_name': 'Trinidad and Tobago',
        'card_link': 'https://www.great.gov.uk/markets/trinidad-and-tobago/',
        'card_title': 'Exporting guide to Trinidad and Tobago',
        'card_content': (
            'One of the wealthiest countries in the Caribbean Community (CARICOM),'
            + ' Trinidad and Tobago has the most active manufacturing sector '
            + 'in the Caribbean and a successful petrochemical industry.'
        ),
    },
    'tunisia': {
        'display_name': 'Tunisia',
        'card_link': 'https://www.great.gov.uk/markets/tunisia/',
        'card_title': 'Exporting guide to Tunisia',
        'card_content': (
            'Tunisia is a North African country and seaboard to the Mediterranean Sea. It is'
            + ' a major gateway to both Europe and Africa. Economic growth is slowly gaining '
            + ' steam with steady GDP growth, which is expected to continue.'
        ),
    },
    'turkey': {
        'display_name': 'Turkey',
        'card_link': 'https://www.great.gov.uk/markets/turkey/',
        'card_title': 'Exporting guide to Turkey',
        'card_content': (
            'Turkey is a large and fascinating market with plenty of export opportunities for UK exporters.'
            + ' It is home to both large multinationals and local businesses with a strong '
            + 'entrepreneurial culture. Despite Turkey’s recent political '
            + 'and economic challenges, the country’s prospects are positive and there is room for growth.'
        ),
    },
    'ukraine': {
        'display_name': 'Ukraine',
        'card_link': 'https://www.great.gov.uk/markets/ukraine/',
        'card_title': 'Exporting guide to Ukraine',
        'card_content': (
            'Strategically located at a crossroads for the European and Asian markets,'
            + ' Ukraine offers a large and developed consumer base, '
            + 'a highly educated workforce, low labour costs and abundant natural resources.'
        ),
    },
    'united arab emirates': {
        'display_name': 'United Arab Emirates',
        'card_link': 'https://www.great.gov.uk/markets/united-arab-emirates/',
        'card_title': 'Exporting guide to United Arab Emirates',
        'card_content': (
            'A key hub on the Arabian Peninsula and Persian Gulf,'
            + " the United Arab Emirates (UAE) is one of the UK's most important trading partners "
            + 'and continues to be a growth market for UK exports.'
        ),
    },
    'united states': {
        'display_name': 'United States',
        'card_link': 'https://www.great.gov.uk/markets/united-states/',
        'card_title': 'Exporting guide to United States',
        'card_content': (
            'The US is the UK’s largest export market for goods and services and the world’s '
            + 'largest economy. With low regulatory barriers, minimal language barriers and '
            + 'access to the global supply chain, it offers huge potential for UK exporters. '
            + 'However, the US is a federal system, not a single national market. This means '
            + 'you will need to treat each state as a separate entity with its own procedures '
            + 'and regulations.'
        ),
    },
    'uruguay': {
        'display_name': 'Uruguay',
        'card_link': 'https://www.great.gov.uk/markets/Uruguay/',
        'card_title': 'Exporting guide to Uruguay',
        'card_content': (
            'Uruguay has an open trade and investment regime, with limited use of non-tariff '
            + 'measures and few border restrictions. It is one of the founding members of the '
            + 'Mercosur trading bloc, alongside Brazil, Argentina and Paraguay.'
        ),
    },
    'vietnam': {
        'display_name': 'Vietnam',
        'card_link': 'https://www.great.gov.uk/markets/vietnam/',
        'card_title': 'Exporting guide to Vietnam',
        'card_content': (
            'Vietnam is one of the world’s fastest growing economies, projected to grow at 6.3 '
            + 'percent in 2023 (World Bank), with growing appetite for UK goods and services. '
            + 'This offers many exciting opportunities for exporters: Vietnam is a market with '
            + '100 million consumers, rising middle class and rapid urbanisation. Vietnam '
            + 'continues to broaden its network of international trade agreements, and proactive '
            + 'government reform is helping to open the market to international business.'
        ),
    },
    'zimbabwe': {
        'display_name': 'Zimbabwe',
        'card_link': 'https://www.great.gov.uk/markets/zimbabwe/',
        'card_title': 'Exporting guide to Zimbabwe',
        'card_content': (
            'Zimbabwe has a tough business environment and is facing significant macro-economic '
            + 'challenges. Nevertheless, investment and export opportunities exist if risks are '
            + 'managed. Anglo American, Unilever, and Standard Chartered are some of the major '
            + 'UK firms in Zimbabwe.'
        ),
    },
}


TASK_VALIDATION_MODAL_TRIGGERS = [
    'Understand how to classify your products',
    'Get the right commodity code',
    'Make a simplified customs declaration',
    'Find a customs agent or fast parcel operator',
    'Claim with Returned Goods Relief (RGR)',
]

SATISFACTION_CHOICES = (
    ('VERY_DISSATISFIED', 'Very dissatisfied'),
    ('DISSATISFIED', 'Dissatisfied'),
    ('NEITHER', 'Neither satisfied nor dissatisfied'),
    ('SATISFIED', 'Satisfied'),
    ('VERY_SATISFIED', 'Very satisfied'),
)

EXPERIENCE_CHOICES = (
    ('NOT_FIND_LOOKING_FOR', 'I did not find what I was looking for'),
    ('DIFFICULT_TO_NAVIGATE', 'I found it difficult to navigate the service'),
    ('SYSTEM_LACKS_FEATURE', 'The service lacks the feature I need'),
    ('UNABLE_TO_LOAD/REFRESH/ENTER', 'I was unable to load/refresh/enter a page'),
    ('OTHER', 'Other'),
    ('NO_ISSUE', 'I did not experience any issues'),
)

USER_JOURNEY_CHOICES = (
    ('ADD_PRODUCT', 'Add Product'),
    ('ARTICLE_PAGE', 'Article Page'),
    ('EXPORT_PLAN_UPDATE', 'Export Plan Update'),
    ('EVENT_BOOKING', 'Event booking'),
    ('COMPANY_VERIFICATION', 'Company verification'),
    ('COMPANY_CONTACT', 'Company contact'),
)

USER_JOURNEY_CHOICES_PRODUCT = (('ADD_PRODUCT', 'Add Product'),)
USER_JOURNEY_CHOICES_LEARN = (('ARTICLE_PAGE', 'Article Page'),)
USER_JOURNEY_CHOICES_EXPORT = (('EXPORT_PLAN_UPDATE', 'Export Plan Update'),)

LIKELIHOOD_CHOICES = (
    ('EXTREMELY_UNLIKELY', 'Extremely unlikely'),
    ('UNLIKELY', 'Unlikely'),
    ('NEITHER_LIKELY_NOR_UNLIKELY', 'Neither likely nor unlikely'),
    ('LIKELY', 'Likely'),
    ('EXTREMELY_LIKELY', 'Extremely likely'),
    ('DONT_KNOW_OR_PREFER_NOT_TO_SAY', "Don't know/prefer not to say"),
)

META_LABELS = (
    ('guidance_great', 'Guidance on great.gov.uk'),
    ('service_great', 'Service on great.gov.uk'),
    ('guidance_gov', 'Guidance on GOV.UK'),
    ('service_gov', 'Service on GOV.UK'),
)

EXPORT_SUPPORT_CATEGORIES = (
    ('/support/market-selection', 'Market selection'),
    ('/support/routes-to-market-and-operating-overseas', 'Routes to market and operating overseas'),
    (
        '/support/funding-and-financial-considerations',
        'Funding and financial considerations',
    ),
    ('/support/trade-restrictions-regulations-and-licensing', 'Trade restrictions, regulations and licensing'),
    ('/support/logistics', 'Logistics'),
    ('/support/customs-taxes-and-declarations', 'Customs, taxes and declarations'),
    ('/support/travelling-for-work', 'Travelling for work'),
    ('/support/managing-business-risk-and-corruption', 'Managing business risk and corruption'),
)

TRADE_BARRIERS_BY_MARKET = {
    'Argentina': '10',
    'Australia': '2',
    'Austria': '1',
    'Bahrain': '1',
    'Bangladesh': '8',
    'Belarus': '2',
    'Bosnia and Herzegovina': '1',
    'Brazil': '14',
    'Canada': '17',
    'Chile': '3',
    'China': '38',
    'Colombia': '13',
    'Costa Rica': '2',
    'Dominican Republic': '2',
    'Ecuador': '1',
    'France': '2',
    'Ghana': '2',
    'Grenada': '1',
    'Guatemala': '1',
    'Honduras': '1',
    'Hong Kong': '3',
    'India': '18',
    'Indonesia': '26',
    'Iran': '1',
    'Israel': '3',
    'Japan': '9',
    'Jordan': '1',
    'Kuwait': '3',
    'Lebanon': '1',
    'Malaysia': '7',
    'Mexico': '6',
    'Mongolia': '4',
    'Morocco': '3',
    'Myanmar': 'Burma',
    'New Zealand': '2',
    'Pakistan': '2',
    'Peru': '4',
    'Poland': '1',
    'Qatar': '5',
    'Romania': '2',
    'Saudi Arabia': '9',
    'Singapore': '2',
    'South Africa': '14',
    'South Korea': '18',
    'Sri Lanka': '4',
    'St Lucia': '1',
    'Taiwan': '4',
    'Thailand': '25',
    'Trinidad and Tobago': '2',
    'Turkmenistan': '5',
    'Ukraine': '3',
    'United Arab Emirates': '5',
    'United States': '23',
    'Uruguay': '2',
    'Uzbekistan': '2',
    'Vietnam': '7',
    'Zimbabwe': '11',
}

TRADE_BARRIERS_BY_SECTOR = {
    'Advanced engineering': '61',
    'Aerospace': '44',
    'Agriculture, horticulture, fisheries and pets': '93',
    'Airports': '56',
    'Automotive': '58',
    'Chemicals': '52',
    'Construction': '66',
    'Consumer and retail': '76',
    'Creative industries': '53',
    'Defence': '45',
    'Education and training': '68',
    'Energy': '73',
    'Environment': '47',
    'Financial and professional services': '100',
    'Food and drink': '124',
    'Healthcare services': '63',
    'Maritime': '51',
    'Medical devices and equipment': '52',
    'Mining': '44',
    'Pharmaceuticals and biotechnology': '74',
    'Railways': '55',
    'Security': '43',
    'Space': '42',
    'Sports economy': '48',
    'Technology and smart cities': '61',
    'Water': '45',
}

EXPORTER_TYPES = (
    ('goods', 'Goods'),
    ('service', 'Service'),
    ('both', 'Both'),
)

CHEG_EXCLUDED_COUNTRY_CODES = [
    'AD',
    'BT',
    'DJ',
    'TL',
    'ER',
    'KI',
    'MW',
    'MV',
    'MH',
    'FM',
    'MC',
    'MN',
    'NR',
    'NP',
    'KP',
    'PW',
    'SM',
    'ST',
    'SO',
    'SS',
    'TO',
    'TV',
    'GB',
    'VU',
    'VA',
    'BF',
    'BI',
    'CV',
    'CF',
    'TD',
    'CD',
    'GQ',
    'GW',
    'NE',
    'RW',
    'SL',
    'GM',
    'ZM',
]


class HCSatStage(Enum):
    NOT_STARTED = 0  # Stage 0: HCSAT has not been started
    SUBMITTED = 1  # Stage 1: HCSAT satisfaction has been submitted
    COMPLETED = 2  # Stage 2: HCSAT has been completed


EU_TRAVEL_ADVICE_URLS = (
    ('Austria', 'https://www.gov.uk/guidance/travel-to-austria-for-work'),
    ('Belgium', 'https://www.gov.uk/guidance/travel-to-belgium-for-work'),
    ('Bulgaria', 'https://www.gov.uk/guidance/travel-to-bulgaria-for-work'),
    ('Croatia', 'https://www.gov.uk/guidance/travel-to-croatia-for-work'),
    ('Cyprus', 'https://www.gov.uk/guidance/travel-to-cyprus-for-work'),
    ('Czechia', 'https://www.gov.uk/guidance/travel-to-the-czech-republic-for-work'),
    ('Denmark', 'https://www.gov.uk/guidance/travel-to-denmark-for-work'),
    ('Estonia', 'https://www.gov.uk/guidance/travel-to-estonia-for-work'),
    ('Finland', 'https://www.gov.uk/guidance/travel-to-finland-for-work'),
    ('France', 'https://www.gov.uk/guidance/travel-to-france-for-work'),
    ('Germany', 'https://www.gov.uk/guidance/travel-to-germany-for-work'),
    ('Greece', 'https://www.gov.uk/guidance/travel-to-greece-for-work'),
    ('Hungary', 'https://www.gov.uk/guidance/travel-to-hungary-for-work'),
    ('Iceland', 'https://www.gov.uk/guidance/travel-to-iceland-for-work'),
    ('Italy', 'https://www.gov.uk/guidance/travel-to-italy-for-work'),
    ('Latvia', 'https://www.gov.uk/guidance/travel-to-latvia-for-work'),
    ('Liechtenstein', 'https://www.gov.uk/guidance/travel-to-liechtenstein-for-work'),
    ('Lithuania', 'https://www.gov.uk/guidance/travel-to-lithuania-for-work'),
    ('Luxembourg', 'https://www.gov.uk/guidance/travel-to-luxembourg-for-work'),
    ('Malta', 'https://www.gov.uk/guidance/travel-to-malta-for-work'),
    ('Netherlands', 'https://www.gov.uk/guidance/travel-to-the-netherlands-for-work'),
    ('Norway', 'https://www.gov.uk/guidance/travel-to-norway-for-work'),
    ('Poland', 'https://www.gov.uk/guidance/travel-to-poland-for-work'),
    ('Portugal', 'https://www.gov.uk/guidance/travel-to-portugal-for-work'),
    ('Romania', 'https://www.gov.uk/guidance/travel-to-romania-for-work'),
    ('Slovakia', 'https://www.gov.uk/guidance/travel-to-slovakia-for-work'),
    ('Slovenia', 'https://www.gov.uk/guidance/travel-to-slovenia-for-work'),
    ('Spain', 'https://www.gov.uk/guidance/travel-to-spain-for-work'),
    ('Sweden', 'https://www.gov.uk/guidance/travel-to-sweden-for-work'),
    ('Switzerland', 'https://www.gov.uk/guidance/travel-to-switzerland-for-work'),
)


class TemplateTagsEnum(Enum):
    EXPORT_ACADEMY_NOTIFY_BOOKING = 0
    EXPORT_ACADEMY_NOTIFY_CANCELLATION = 1
    EXPORT_ACADEMY_NOTIFY_EVENT_REMINDER = 2
    EXPORT_ACADEMY_NOTIFY_FOLLOW_UP = 3
    EXPORT_ACADEMY_NOTIFY_REGISTRATION = 4
    GOV_NOTIFY_ALREADY_REGISTERED = 5
    EYB_INCOMPLETE_TRIAGE_REMINDER = 6
    EYB_ENROLMENT_WELCOME = 7
    CONFIRM_VERIFICATION_CODE = 8


# True equates to settings.FEATURE_USE_BGS_TEMPLATES being True
# False equates to settings.FEATURE_USE_BGS_TEMPLATES being False
TEMPLATE_TAGS = {
    True: {
        TemplateTagsEnum.EXPORT_ACADEMY_NOTIFY_BOOKING: settings.BGS_EXPORT_ACADEMY_NOTIFY_BOOKING_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.EXPORT_ACADEMY_NOTIFY_CANCELLATION: settings.BGS_EXPORT_ACADEMY_NOTIFY_CANCELLATION_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.EXPORT_ACADEMY_NOTIFY_EVENT_REMINDER: settings.BGS_EXPORT_ACADEMY_NOTIFY_EVENT_REMINDER_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.EXPORT_ACADEMY_NOTIFY_FOLLOW_UP: settings.BGS_EXPORT_ACADEMY_NOTIFY_FOLLOW_UP_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.EXPORT_ACADEMY_NOTIFY_REGISTRATION: settings.BGS_EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.GOV_NOTIFY_ALREADY_REGISTERED: settings.BGS_GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.EYB_INCOMPLETE_TRIAGE_REMINDER: settings.BGS_EYB_INCOMPLETE_TRIAGE_REMINDER_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.EYB_ENROLMENT_WELCOME: settings.BGS_EYB_ENROLMENT_WELCOME_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.CONFIRM_VERIFICATION_CODE: settings.BGS_CONFIRM_VERIFICATION_CODE_TEMPLATE_ID,  # noqa E501
    },
    False: {
        TemplateTagsEnum.EXPORT_ACADEMY_NOTIFY_BOOKING: settings.EXPORT_ACADEMY_NOTIFY_BOOKING_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.EXPORT_ACADEMY_NOTIFY_CANCELLATION: settings.EXPORT_ACADEMY_NOTIFY_CANCELLATION_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.EXPORT_ACADEMY_NOTIFY_EVENT_REMINDER: settings.EXPORT_ACADEMY_NOTIFY_EVENT_REMINDER_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.EXPORT_ACADEMY_NOTIFY_FOLLOW_UP: settings.EXPORT_ACADEMY_NOTIFY_FOLLOW_UP_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.EXPORT_ACADEMY_NOTIFY_REGISTRATION: settings.EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.GOV_NOTIFY_ALREADY_REGISTERED: settings.GOV_NOTIFY_ALREADY_REGISTERED_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.EYB_INCOMPLETE_TRIAGE_REMINDER: settings.EYB_INCOMPLETE_TRIAGE_REMINDER_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.EYB_ENROLMENT_WELCOME: settings.EYB_ENROLMENT_WELCOME_TEMPLATE_ID,  # noqa E501
        TemplateTagsEnum.CONFIRM_VERIFICATION_CODE: settings.CONFIRM_VERIFICATION_CODE_TEMPLATE_ID,  # noqa E501
    },
}
