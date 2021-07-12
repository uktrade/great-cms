COMPANIES_HOUSE_COMPANY = 'companies-house-company'
NON_COMPANIES_HOUSE_COMPANY = 'non-companies-house-company'
NOT_COMPANY = 'not-company'
OVERSEAS_COMPANY = 'overseas-company'

# companies that have companies house numbers prefixed with below do not have address in companies house
COMPANY_NUMBER_PREFIXES_INCOMPLETE_INFO = (
    'IP',  # Industrial & Provident Company
    'SP',  # Scottish Industrial/Provident Company
    'IC',  # ICVC
    'SI',  # Scottish ICVC
    'RS',  # Registered Society
    'NP',  # Northern Ireland Industrial/Provident Company or Credit Union
    'NV',  # Northern Ireland ICVC
    'RC',  # Royal Charter Company
    'SR',  # Scottish Royal Charter Company
    'NR',  # Northern Ireland Royal Charter Company
    'CS',  # Scottish charitable incorporated organisation
    'CE',  # Charitable incorporated organisation
)

# Enrollment view constants
SESSION_KEY_ENROL_KEY = 'ENROL_KEY'
SESSION_KEY_ENROL_KEY_COMPANY_DATA = 'ENROL_KEY_COMPANY_DATA'
SESSION_KEY_INGRESS_ANON = 'ANON_INGRESS'
SESSION_KEY_COMPANY_CHOICE = 'COMPANY_CHOICE'
SESSION_KEY_COMPANY_DATA = 'ENROL_KEY_COMPANY_DATA'
SESSION_KEY_REFERRER = 'REFERRER_URL'
SESSION_KEY_BUSINESS_PROFILE_INTENT = 'BUSINESS_PROFILE_INTENT'
SESSION_KEY_BACKFILL_DETAILS_INTENT = 'BACKFILL_DETAILS_INTENT'
SESSION_KEY_EXPORT_OPPORTUNITY_INTENT = 'EXPORT_OPPORTUNITY_INTENT'
SESSION_KEY_INVITE_KEY = 'INVITE_KEY'

PROGRESS_STEP_LABEL_USER_ACCOUNT = 'Enter your business email address and set a password'
PROGRESS_STEP_LABEL_INDIVIDUAL_USER_ACCOUNT = 'Enter your email address and set a password'
PROGRESS_STEP_LABEL_VERIFICATION = 'Enter your confirmation code'
PROGRESS_STEP_LABEL_RESEND_VERIFICATION = 'Resend verification'
PROGRESS_STEP_LABEL_PERSONAL_INFO = 'Enter your personal details'
PROGRESS_STEP_LABEL_BUSINESS_TYPE = 'Select your business type'
PROGRESS_STEP_LABEL_BUSINESS_DETAILS = 'Enter your business details'

RESEND_VERIFICATION = 'resend'
USER_ACCOUNT = 'user-account'
VERIFICATION = 'verification'
COMPANY_SEARCH = 'company-search'
ADDRESS_SEARCH = 'address-search'
BUSINESS_INFO = 'business-details'
PERSONAL_INFO = 'personal-details'
FINISHED = 'finished'
FAILURE = 'failure'
INVITE_EXPIRED = 'invite-expired'
