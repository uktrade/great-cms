const countries = [
  'Abu Dhabi',
  'Afghanistan',
  'Ajman',
  'Akrotiri',
  'Åland Islands',
  'Albania',
  'Algeria',
  'American Samoa',
  'Andorra',
  'Angola',
  'Anguilla',
  'Antigua and Barbuda',
  'Argentina',
  'Armenia',
  'Aruba',
  'Ascension',
  'Australia',
  'Austria',
  'Azerbaijan',
  'Bahrain',
  'Baker Island',
  'Bangladesh',
  'Barbados',
  'Belarus',
  'Belgium',
  'Belize',
  'Benin',
  'Bermuda',
  'Bhutan',
  'Bolivia',
  'Bonaire',
  'Bosnia and Herzegovina',
  'Botswana',
  'Brazil',
  'British Indian Ocean Territory',
  'British Virgin Islands',
  'Brunei',
  'Bulgaria',
  'Burkina Faso',
  'Burundi',
  'Cambodia',
  'Cameroon',
  'Canada',
  'Cape Verde',
  'Cayman Islands',
  'Central African Republic',
  'Ceuta',
  'Chad',
  'Chile',
  'China',
  'Christmas Island',
  'Cocos (Keeling) Islands',
  'Colombia',
  'Comoros',
  'Congo',
  'Congo (Democratic Republic)',
  'Cook Islands',
  'Costa Rica',
  'Croatia',
  'Cuba',
  'Curaçao',
  'Cyprus',
  'Czechia',
  'Denmark',
  'Dhekelia',
  'Djibouti',
  'Dominica',
  'Dominican Republic',
  'Dubai',
  'East Timor',
  'Ecuador',
  'Egypt',
  'El Salvador',
  'Equatorial Guinea',
  'Eritrea',
  'Estonia',
  'Eswatini',
  'Ethiopia',
  'Falkland Islands',
  'Faroe Islands',
  'Fiji',
  'Finland',
  'France',
  'French Guiana',
  'French Polynesia',
  'Fujairah',
  'Gabon',
  'Georgia',
  'Germany',
  'Ghana',
  'Gibraltar',
  'Greece',
  'Greenland',
  'Grenada',
  'Guadeloupe',
  'Guam',
  'Guatemala',
  'Guernsey',
  'Guinea',
  'Guinea-Bissau',
  'Guyana',
  'Haiti',
  'Honduras',
  'Hong Kong',
  'Howland Island',
  'Hungary',
  'Iceland',
  'India',
  'Indonesia',
  'Iran',
  'Iraq',
  'Ireland',
  'Isle of Man',
  'Israel',
  'Italy',
  'Ivory Coast',
  'Jamaica',
  'Japan',
  'Jarvis Island',
  'Jersey',
  'Johnston Atoll',
  'Jordan',
  'Kazakhstan',
  'Kenya',
  'Kingman Reef',
  'Kiribati',
  'Kosovo',
  'Kuwait',
  'Kyrgyzstan',
  'Laos',
  'Latvia',
  'Lebanon',
  'Lesotho',
  'Liberia',
  'Libya',
  'Liechtenstein',
  'Lithuania',
  'Luxembourg',
  'Macao',
  'Madagascar',
  'Malawi',
  'Malaysia',
  'Maldives',
  'Mali',
  'Malta',
  'Marshall Islands',
  'Martinique',
  'Mauritania',
  'Mauritius',
  'Mayotte',
  'Melilla',
  'Mexico',
  'Micronesia',
  'Midway Islands',
  'Moldova',
  'Monaco',
  'Mongolia',
  'Montenegro',
  'Montserrat',
  'Morocco',
  'Mozambique',
  'Myanmar (Burma)',
  'Namibia',
  'Nauru',
  'Navassa Island',
  'Nepal',
  'Netherlands',
  'New Caledonia',
  'New Zealand',
  'Nicaragua',
  'Niger',
  'Nigeria',
  'Niue',
  'Norfolk Island',
  'Northern Mariana Islands',
  'North Korea',
  'North Macedonia',
  'Norway',
  'Occupied Palestinian Territories',
  'Oman',
  'Pakistan',
  'Palau',
  'Palmyra Atoll',
  'Panama',
  'Papua New Guinea',
  'Paraguay',
  'Peru',
  'Philippines',
  'Pitcairn, Henderson, Ducie and Oeno Islands',
  'Poland',
  'Portugal',
  'Puerto Rico',
  'Qatar',
  'Ras al-Khaimah',
  'Réunion',
  'Romania',
  'Russia',
  'Rwanda',
  'Saba',
  'Saint Barthélemy',
  'Saint Helena',
  'Saint-Martin (French part)',
  'Saint Pierre and Miquelon',
  'Samoa',
  'San Marino',
  'Sao Tome and Principe',
  'Saudi Arabia',
  'Senegal',
  'Serbia',
  'Seychelles',
  'Sharjah',
  'Sierra Leone',
  'Singapore',
  'Sint Eustatius',
  'Sint Maarten (Dutch part)',
  'Slovakia',
  'Slovenia',
  'Solomon Islands',
  'Somalia',
  'South Africa',
  'South Georgia and South Sandwich Islands',
  'South Korea',
  'South Sudan',
  'Spain',
  'Sri Lanka',
  'St Kitts and Nevis',
  'St Lucia',
  'St Vincent',
  'Sudan',
  'Suriname',
  'Svalbard and Jan Mayen',
  'Sweden',
  'Switzerland',
  'Syria',
  'Taiwan',
  'Tajikistan',
  'Tanzania',
  'Thailand',
  'The Bahamas',
  'The Gambia',
  'Togo',
  'Tokelau',
  'Tonga',
  'Trinidad and Tobago',
  'Tristan da Cunha',
  'Tunisia',
  'Turkey',
  'Turkmenistan',
  'Turks and Caicos Islands',
  'Tuvalu',
  'Uganda',
  'Ukraine',
  'Umm al-Quwain',
  'United Arab Emirates',
  'United Kingdom',
  'United States',
  'United States Virgin Islands',
  'Uruguay',
  'Uzbekistan',
  'Vanuatu',
  'Vatican City',
  'Venezuela',
  'Vietnam',
  'Wake Island',
  'Wallis and Futuna',
  'Western Sahara',
  'Yemen',
  'Zambia',
  'Zimbabwe',
]

const countryISO2CodeToName = {
  'AU': 'Australia',
  'AZ': 'Azerbaijan',
  'BH': 'Bahrain',
  'UM-81': 'Baker Island',
  'BD': 'Bangladesh',
  'BB': 'Barbados',
  'BY': 'Belarus',
  'BE': 'Belgium',
  'BZ': 'Belize',
  'BJ': 'Benin',
  'BM': 'Bermuda',
  'BT': 'Bhutan',
  'BO': 'Bolivia',
  'BQ-BO': 'Bonaire',
  'BA': 'Bosnia and Herzegovina',
  'BW': 'Botswana',
  'BR': 'Brazil',
  'IO': 'British Indian Ocean Territory',
  'CA': 'Canada',
  'CV': 'Cape Verde',
  'KY': 'Cayman Islands',
  'ES-CE': 'Ceuta',
  'TD': 'Chad',
  'CL': 'Chile',
  'CN': 'China',
  'CX': 'Christmas Island',
  'CC': 'Cocos (Keeling) Islands',
  'CO': 'Colombia',
  'KM': 'Comoros',
  'CG': 'Congo',
  'CD': 'Congo (Democratic Republic)',
  'CK': 'Cook Islands',
  'CR': 'Costa Rica',
  'HR': 'Croatia',
  'CU': 'Cuba',
  'CW': 'Curaçao',
  'CY': 'Cyprus',
  'DM': 'Dominica',
  'DO': 'Dominican Republic',
  'AE-DU': 'Dubai',
  'TL': 'East Timor',
  'EC': 'Ecuador',
  'EG': 'Egypt',
  'SV': 'El Salvador',
  'GQ': 'Equatorial Guinea',
  'ER': 'Eritrea',
  'EE': 'Estonia',
  'SZ': 'Eswatini',
  'ET': 'Ethiopia',
  'FK': 'Falkland Islands',
  'FO': 'Faroe Islands',
  'FJ': 'Fiji',
  'FI': 'Finland',
  'FR': 'France',
  'GF': 'French Guiana',
  'PF': 'French Polynesia',
  'AE-FU': 'Fujairah',
  'GA': 'Gabon',
  'GE': 'Georgia',
  'DE': 'Germany',
  'GH': 'Ghana',
  'GI': 'Gibraltar',
  'GR': 'Greece',
  'GL': 'Greenland',
  'GG': 'Guernsey',
  'GN': 'Guinea',
  'GW': 'Guinea-Bissau',
  'GY': 'Guyana',
  'HT': 'Haiti',
  'HN': 'Honduras',
  'HK': 'Hong Kong',
  'UM-84': 'Howland Island',
  'HU': 'Hungary',
  'IS': 'Iceland',
  'IN': 'India',
  'ID': 'Indonesia',
  'IR': 'Iran',
  'IQ': 'Iraq',
  'IE': 'Ireland',
  'IM': 'Isle of Man',
  'IL': 'Israel',
  'IT': 'Italy',
  'CI': 'Ivory Coast',
  'JM': 'Jamaica',
  'JP': 'Japan',
  'UM-86': 'Jarvis Island',
  'JE': 'Jersey',
  'UM-67': 'Johnston Atoll',
  'JO': 'Jordan',
  'KZ': 'Kazakhstan',
  'KE': 'Kenya',
  'UM-89': 'Kingman Reef',
  'KI': 'Kiribati',
  'XK': 'Kosovo',
  'KW': 'Kuwait',
  'KG': 'Kyrgyzstan',
  'LA': 'Laos',
  'LV': 'Latvia',
  'LB': 'Lebanon',
  'LS': 'Lesotho',
  'LR': 'Liberia',
  'LY': 'Libya',
  'LI': 'Liechtenstein',
  'MY': 'Malaysia',
  'MV': 'Maldives',
  'ML': 'Mali',
  'MT': 'Malta',
  'MH': 'Marshall Islands',
  'MQ': 'Martinique',
  'MR': 'Mauritania',
  'MU': 'Mauritius',
  'YT': 'Mayotte',
  'ES-ML': 'Melilla',
  'MX': 'Mexico',
  'UM-71': 'Midway Islands',
  'MD': 'Moldova',
  'MC': 'Monaco',
  'MN': 'Mongolia',
  'ME': 'Montenegro',
  'MS': 'Montserrat',
  'MA': 'Morocco',
  'MZ': 'Mozambique',
  'MM': 'Myanmar (Burma)',
  'NA': 'Namibia',
  'NR': 'Nauru',
  'UM-76': 'Navassa Island',
  'NP': 'Nepal',
  'NL': 'Netherlands',
  'NC': 'New Caledonia',
  'NZ': 'New Zealand',
  'NI': 'Nicaragua',
  'NE': 'Niger',
  'NG': 'Nigeria',
  'NU': 'Niue',
  'NF': 'Norfolk Island',
  'MP': 'Northern Mariana Islands',
  'KP': 'North Korea',
  'MK': 'North Macedonia',
  'NO': 'Norway',
  'PS': 'Occupied Palestinian Territories',
  'OM': 'Oman',
  'PK': 'Pakistan',
  'PW': 'Palau',
  'UM-95': 'Palmyra Atoll',
  'PA': 'Panama',
  'PG': 'Papua New Guinea',
  'PY': 'Paraguay',
  'PE': 'Peru',
  'PH': 'Philippines',
  'PN': 'Pitcairn, Henderson, Ducie and Oeno Islands',
  'PL': 'Poland',
  'PT': 'Portugal',
  'PR': 'Puerto Rico',
  'QA': 'Qatar',
  'AE-RK': 'Ras al-Khaimah',
  'RE': 'Réunion',
  'RO': 'Romania',
  'RU': 'Russia',
  'RW': 'Rwanda',
  'BQ-SA': 'Saba',
  'BL': 'Saint Barthélemy',
  'SH-HL': 'Saint Helena',
  'MF': 'Saint-Martin (French part)',
  'PM': 'Saint Pierre and Miquelon',
  'AE-SH': 'Sharjah',
  'SG': 'Singapore',
  'BQ-SE': 'Sint Eustatius',
  'SX': 'Sint Maarten (Dutch part)',
  'SK': 'Slovakia',
  'SI': 'Slovenia',
  'ES': 'Spain',
  'LK': 'Sri Lanka',
  'KN': 'St Kitts and Nevis',
  'LC': 'St Lucia',
  'VC': 'St Vincent',
  'SD': 'Sudan',
  'SR': 'Suriname',
  'SJ': 'Svalbard and Jan Mayen',
  'SE': 'Sweden',
  'CH': 'Switzerland',
  'SY': 'Syria',
  'TW': 'Taiwan',
  'TJ': 'Tajikistan',
  'TZ': 'Tanzania',
  'TH': 'Thailand',
  'BS': 'The Bahamas',
  'GM': 'The Gambia',
  'TG': 'Togo',
  'TK': 'Tokelau',
  'TO': 'Tonga',
  'TT': 'Trinidad and Tobago',
  'SH-TA': 'Tristan da Cunha',
  'TN': 'Tunisia',
  'TR': 'Turkey',
  'TM': 'Turkmenistan',
  'TC': 'Turks and Caicos Islands',
  'TV': 'Tuvalu',
  'UG': 'Uganda',
  'UA': 'Ukraine',
  'AE-UQ': 'Umm al-Quwain',
  'AE': 'United Arab Emirates',
  'GB': 'United Kingdom',
  'US': 'United States',
  'VI': 'United States Virgin Islands',
  'UY': 'Uruguay',
  'UZ': 'Uzbekistan',
  'VU': 'Vanuatu',
  'VA': 'Vatican City',
  'UM-79': 'Wake Island',
  'WF': 'Wallis and Futuna',
  'EH': 'Western Sahara',
  'YE': 'Yemen',
  'ZM': 'Zambia',
  'ZW': 'Zimbabwe',
  'AE-AZ': 'Abu Dhabi',
  'AF': 'Afghanistan',
  'AE-AJ': 'Ajman',
  'XQZ': 'Akrotiri',
  'AX': 'Åland Islands',
  'AL': 'Albania',
  'DZ': 'Algeria',
  'AS': 'American Samoa',
  'AD': 'Andorra',
  'AO': 'Angola',
  'AI': 'Anguilla',
  'AG': 'Antigua and Barbuda',
  'AR': 'Argentina',
  'AM': 'Armenia',
  'AW': 'Aruba',
  'SH-AC': 'Ascension',
  'AT': 'Austria',
  'VG': 'British Virgin Islands',
  'BN': 'Brunei',
  'BG': 'Bulgaria',
  'BF': 'Burkina Faso',
  'BI': 'Burundi',
  'KH': 'Cambodia',
  'CM': 'Cameroon',
  'CZ': 'Czechia',
  'DK': 'Denmark',
  'XXD': 'Dhekelia',
  'DJ': 'Djibouti',
  'FM': 'Federated States of Micronesia’',
  'LT': 'Lithuania',
  'LU': 'Luxembourg',
  'MO': 'Macao',
  'MG': 'Madagascar',
  'MW': 'Malawi',
  'WS': 'Samoa',
  'SM': 'San Marino',
  'ST': 'Sao Tome and Principe',
  'SA': 'Saudi Arabia',
  'SN': 'Senegal',
  'RS': 'Serbia',
  'SC': 'Seychelles',
  'SL': 'Sierra Leone',
  'SB': 'Solomon Islands',
  'SO': 'Somalia',
  'ZA': 'South Africa',
  'GS': 'South Georgia and South Sandwich Islands',
  'KR': 'South Korea',
  'SS': 'South Sudan',
  'GD': 'Grenada',
  'GP': 'Guadeloupe',
  'GU': 'Guam',
  'GT': 'Guatemala',
  'VE': 'Venezuela',
  'VN': 'Vietnam',
  'CF': 'Central African Republic'
}
