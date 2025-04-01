LESS_THAN_3_YEARS_AGO = 'LESS_THAN_3_YEARS_AGO'
MORE_THAN_3_YEARS_AGO = 'MORE_THAN_3_YEARS_AGO'

EXISTING_BUSINESS_WHEN_SET_UP_CHOICES = (
    (LESS_THAN_3_YEARS_AGO, 'Less than 3 years ago'),
    (MORE_THAN_3_YEARS_AGO, 'More than 3 years ago'),
)

EXISTING_BUSINESS_TURNOVER_CHOICES = (
    ('LESS_THAN_90K', 'Less than £90,000'),
    ('90K_TO_500K', '£90,000 to £500,000'),
    ('500k_TO_2M', '£500,000 to £2 million'),
    ('2M_TO_5M', '£2 million to £5 million'),
    ('5M_TO_10M', '£5 million to £10 million'),
    ('10M_PLUS', 'Over £10 million'),
    ('PREFER_NOT_TO_SAY', 'Prefer not to say'),
)
