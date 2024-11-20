def get_step_guide_accordion_items():
    items = [
        {
            'heading': {'text': 'Set up your business'},
            'summary': {'text': "Choose how you'll operate, and register your company in as little as a day."},
            'content': {
                'html': (
                    '<p class="govuk-body">'
                    'You could operate as a private limited UK company, an overseas branch of your existing '
                    "company, or perhaps a joint venture with a UK business. You'll need to choose before "
                    'registering.'
                    '</p>'
                    '<p class="govuk-body">'
                    'You must register your company with Companies House, the government organisation '
                    'responsible for registration of companies in the UK, if you want to set up a place of '
                    'business in the UK.'
                    '</p>'
                    '<p class="govuk-body">'
                    '<a class="govuk-link" href="/international/expand-your-business-in-the-uk/guide/'
                    '    detailed-guides/set-up-and-register-your-business">'
                    'Read our guide on how to set up and register your business'
                    '</a>'
                    '</p>'
                )
            },
        },
        {
            'heading': {'text': 'Apply for visas'},
            'summary': {
                'text': 'There are a range of business-related visas available, and a decision can take '
                'from 3 to 11 weeks.'
            },
            'content': {
                'html': (
                    '<p class="govuk-body">'
                    'A visa application decision takes 3 weeks on average, if it does not involve '
                    'endorsement or sponsorship.'
                    '</p>'
                    '<p class="govuk-body">'
                    'If an endorsement is needed, the process can take up to 7 weeks in total. If '
                    'sponsorship is needed, this process plus the visa application can take around 11 '
                    'weeks in total.'
                    '</p>'
                    '<p class="govuk-body">'
                    'You may or may not need to apply for a visa, depending on your circumstances and '
                    'planned business activities.'
                    '</p>'
                    '<p class="govuk-body">'
                    '<a class="govuk-link" href="/international/expand-your-business-in-the-uk/guide/'
                    '    detailed-guides/how-to-apply-for-a-visa">'
                    'Read our guide on visa types'
                    '</a>'
                    '</p>'
                    '<p class="govuk-body">'
                    '<a class="govuk-link" href="https://www.gov.uk/check-uk-visa">'
                    'Check if you need a visa on GOV.UK'
                    '</a>'
                    '</p>'
                )
            },
        },
        {
            'heading': {'text': 'Open a business bank account'},
            'summary': {
                'text': 'You can get a digital account in a matter of hours, or a full business account '
                'in 1 to 3 months.'
            },
            'content': {
                'html': (
                    '<p class="govuk-body">'
                    "You'll need a UK business bank account to trade in the UK. You can choose between "
                    'traditional banks and digital-only banks.'
                    '</p>'
                    '<p class="govuk-body">'
                    'Digital-only banks can open accounts in hours or days, but may have limited services. '
                    'Traditional banks take longer but offer a full range of business banking services.'
                    '</p>'
                    '<p class="govuk-body">'
                    '<a class="govuk-link" href="/international/expand-your-business-in-the-uk/guide/'
                    '    detailed-guides/open-a-business-bank-account">'
                    'Read our guide on business banking'
                    '</a>'
                    '</p>'
                )
            },
        },
        {
            'heading': {'text': 'Find the right location and premises'},
            'summary': {
                'text': "Once you've found a property, it can take as little as 1 week to lease or "
                '1 to 4 months to buy one.'
            },
            'content': {
                'html': (
                    '<p class="govuk-body">'
                    'A suitable location near to customers, staff and supply chains, is important to your '
                    'success in the UK.'
                    '</p>'
                    '<p class="govuk-body">'
                    'You can find a range of premises to suit your business including leased offices, '
                    'co-working spaces and science parks.'
                    '</p>'
                    '<p class="govuk-body">'
                    '<a class="govuk-link" href="/international/expand-your-business-in-the-uk/guide/'
                    '    detailed-guides/find-the-right-location-and-premises">'
                    'Read our guide on how to find the right business property'
                    '</a>'
                    '</p>'
                    '<p class="govuk-body">'
                    '<a class="govuk-link" href="https://www.great.gov.uk/international/content/'
                    '    investment/regions/" target="_blank">'
                    "Learn more about the UK's nations and regions"
                    '</a>'
                    '</p>'
                    '<p class="govuk-body">'
                    '<a class="govuk-link" href="https://www.great.gov.uk/international/'
                    '    investment-support-directory" target="_blank">'
                    'Find professional help to locate in the UK'
                    '</a>'
                    '</p>'
                )
            },
        },
        {
            'heading': {'text': 'Get business insurance'},
            'summary': {'text': "You'll need to obtain cover for various parts of your business."},
            'content': {
                'html': (
                    '<p class="govuk-body">'
                    "You must get Employers' Liability insurance as soon as you become an employer. UK "
                    'law also requires you to have third party motor insurance if you use a vehicle for '
                    'business purposes.'
                    '</p>'
                    '<p class="govuk-body">'
                    'Other things which might have to be insured includes assets, income, liabilities '
                    'and people.'
                    '</p>'
                    '<p class="govuk-body">'
                    '<a class="govuk-link" href="https://www.gov.uk/employers-liability-insurance" '
                    '    target="_blank">'
                    "Employers' Liability Insurance on GOV.UK"
                    '</a>'
                    '</p>'
                    '<p class="govuk-body">'
                    '<a class="govuk-link" href="https://www.great.gov.uk/international/'
                    '    investment-support-directory" target="_blank">'
                    'Find professional advice on business insurance'
                    '</a>'
                    '</p>'
                    '<p class="govuk-body">'
                    'It can take around 2 weeks to 1 month to arrange business insurance.'
                    '</p>'
                )
            },
        },
    ]

    return {'items': items, 'id': 'accordion-default', 'classes': ''}
