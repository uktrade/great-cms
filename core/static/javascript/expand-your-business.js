function onSubmitSector() {
  if (!document.getElementById('js-sector-select').value)
    document.getElementById('js-sector-select-select').value = '';
}

function onSubmitLocation() {
  if (!document.getElementById('js-location-select').value)
    document.getElementById('js-location-select-select').value = '';
}

function onSubmitProfile() {
  if (!document.getElementById('js-company-location-select').value)
    document.getElementById('js-company-location-select-select').value = '';
}

function handleSpendRadioClick(radio) {
  if (otherRadioElement.checked == false) {
    document.getElementById('id_spend_other').value = '';
  }
}

// the autocomplete library we use has a known accessability issue when ESC is pressed
// (see https://github.com/alphagov/accessible-autocomplete/issues/692)

function showDropdown(dropdownElement, show) {
  if (show == true) {
    dropdownElement.classList.remove('autocomplete__menu--hidden')
    dropdownElement.classList.add('autocomplete__menu--visibile')
  } else {
    dropdownElement.classList.remove('autocomplete__menu--visible')
    dropdownElement.classList.add('autocomplete__menu--hidden')
  }
}

function focusInput(textInputElement) {
  textInputElement.focus()
  textInputElement.classList.add('autocomplete__input--focused')
}

function setCaretPositionToEnd(textInputElement) {
  const lenText = textInputElement.value.length
  textInputElement.setSelectionRange(lenText, lenText)
}


function autocompleteFocusOnESC(parentInputID, dropdownID) {
  const parentInput = document.querySelector(parentInputID)
  const dropdown = document.querySelector(dropdownID)
  // setTimeout is used because the autocomplete library sets the focused element to null on press of ESC via
  // https://github.com/alphagov/accessible-autocomplete/blob/79370c8c66f7496fb503bb1840cd590157f97232/src/autocomplete.js#L175 # /PS-IGNORE
  dropdown.addEventListener('keydown', (e) => {
    if (e.key == 'Escape') {
      setTimeout(() => {
        focusInput(parentInput)
      }, 1)
      setTimeout(() => {
        showDropdown(dropdown, false)
        setCaretPositionToEnd(parentInput)
      }, 1)
    }
  })
  parentInput.addEventListener('keydown', (e) => {
    // user presses esc on text input element (mouse navigation to select dropdown elements)
    if (e.key == 'Escape') {
      setTimeout(() => {
        focusInput(parentInput)
      }, 1)
    } else if (e.key != 'Tab') {
      // user has started typing again so show dropdown if num chars > 2 (value used when initilising auto complete library)
      setTimeout(() => {
        show = parentInput.value.length > 2
        showDropdown(dropdown, show)
      }, 1)
    }
  })
}

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
