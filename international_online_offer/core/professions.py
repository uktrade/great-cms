from directory_constants import sectors as directory_constants_sectors
from international_online_offer.core import sectors

ENTRY_LEVEL = 'Entry-level'
MID_SENIOR_LEVEL = 'Middle/Senior Management'
DIRECTOR_EXECUTIVE_LEVEL = 'Director/Executive'

PROFESSIONS_BY_SECTOR_AND_LEVEL = [
    {
        'sector': directory_constants_sectors.FOOD_AND_DRINK,
        'entry_level': 'bartenders, waiting staff and cooks',
        'mid_level': 'chefs and catering managers',
        'executive_level': 'senior restaurant managers and food company chief executives',
    },
    {
        'sector': sectors.TECHNOLOGY_AND_SMART_CITIES,
        'entry_level': 'IT user support, IT operations technicians and electricians',
        'mid_level': 'electronic engineers and IT project managers',
        'executive_level': 'senior managers, IT directors and chief executives',
    },
    {
        'sector': directory_constants_sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES,
        'entry_level': 'finance officers, personal assistants and payroll managers',
        'mid_level': 'accountants, business analysts and solicitors',
        'executive_level': 'directors, vice presidents and chief executives',
    },
    {
        'sector': directory_constants_sectors.CONSUMER_AND_RETAIL,
        'entry_level': 'sales assistants, cashiers and telephone salespeople',
        'mid_level': 'retail managers and hair and beauty salon managers',
        'executive_level': 'senior retail managers, directors and chief executives',
    },
    {
        'sector': sectors.CREATIVE_INDUSTRIES,
        'entry_level': 'graphic designers, dressmakers and translators',
        'mid_level': 'public relations managers, advertising managers and web professionals',
        'executive_level': 'marketing directors and advertising directors',
    },
]
