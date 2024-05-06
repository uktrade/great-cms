LIMITED = 'LIMITED'
COMPANY_TYPE_CHOICES = (
    (LIMITED, 'UK private or public limited company'),
    ('OTHER', 'Other type of UK organisation'),
)
COMPANY_TYPE_OTHER_CHOICES = (
    ('CHARITY', 'Charity'),
    ('GOVERNMENT_DEPARTMENT', 'Government department'),
    ('INTERMEDIARY', 'Intermediary'),
    ('LIMITED_PARTNERSHIP', 'Limited partnership'),
    ('SOLE_TRADER', 'Sole Trader'),
    ('FOREIGN', 'UK branch of foreign company'),
    ('OTHER', 'Other'),
)

HMRC = 'HMRC'
DEFRA = 'Defra'
BEIS = 'BEIS'
IMPORT_CONTROLS = 'import-controls'
TRADE_WITH_UK_APP = 'trade-with-uk-app'
EXPORTING_TO_UK = 'exporting-to-uk'

BUYING = 'buying'
DOMESTIC = 'domestic'
DSO = 'dso'
EVENTS = 'events'
EXPORT_ADVICE = 'export-advice'
EXPORT_OPPORTUNITIES = 'export-opportunities'
EXPORTING = 'exporting'
FINANCE = 'finance'
GREAT_ACCOUNT = 'great-account'
GREAT_SERVICES = 'great-services'
INTERNATIONAL = 'international'
INVESTING = 'investing'
CAPITAL_INVEST = 'capital-invest'
LOCATION = 'location'
OTHER = 'other'
TRADE_OFFICE = 'trade-office'
ALERTS = 'alerts'
NO_RESPONSE = 'no-response'

NO_VERIFICATION_EMAIL = 'no-email-confirmation'
PASSWORD_RESET = 'password-reset'
COMPANIES_HOUSE_LOGIN = 'companies-house-login'
COMPANY_NOT_FOUND = 'company-not-found'
VERIFICATION_CODE = 'verification-code'
NO_VERIFICATION_LETTER = 'no-verification-letter'
NO_VERIFICATION_MISSING = 'verification-missing'


MARKETING_SOURCES_CHOICES = (
    ('From an International Trade Advisor in my region', 'From an International Trade Advisor in my region'),
    ('I saw this being promoted online', 'I saw this being promoted online'),
    ('I read about this in the press', 'I read about this in the press'),
    ('I was searching for export advice online', 'I was searching for export advice online'),
    ('I received an email', 'I received an email'),
    ('Export Support Service', 'Export Support Service'),
    ('Growth hubs', 'Growth hubs'),
    ('Local Enterprise Partnership', 'Local Enterprise Partnership'),
    ('Chamber of Commerce', 'Chamber of Commerce'),
    ('Other', 'Other'),
)


CONTACT_FORM_INDUSTRIES = [
    'Advanced engineering',
    'Aerospace',
    'Agriculture, horticulture, fisheries and pets',
    'Airports',
    'Automotive',
    'Chemicals',
    'Construction',
    'Consumer and retail',
    'Creative industries',
    'Defence',
    'Education and training',
    'Energy',
    'Environment',
    'Financial and professional services',
    'Food and drink',
    'Healthcare services',
    'Logistics',
    'Maritime',
    'Medical devices and equipment',
    'Mining',
    'Pharmaceuticals and biotechnology',
    'Railways',
    'Security',
    'Space',
    'Sports economy',
    'Technology and smart cities',
    'Water',
]

INDUSTRY_CHOICES = [('', 'Please select')] + [(item, item) for item in CONTACT_FORM_INDUSTRIES] + [('OTHER', 'Other')]

INDUSTRY_MAP = dict(INDUSTRY_CHOICES)

I_EXPORT_ALREADY = 'I_EXPORT_ALREADY'
I_AM_INTERESTED_IN_EXPORTING = 'I_AM_INTERESTED_IN_EXPORTING'
FUTURE_FTAS_CHOICE = 'Future FTAs'
