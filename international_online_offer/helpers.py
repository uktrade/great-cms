def get_step_guide_accordion_items():
    items = [
        {
            'heading': {'text': 'Set up your business'},
            'summary': {'text': "Choose how you'll operate, and register your company in as little as a day."},
            'content': {
                'html': (
                    f'{"""<p class="govuk-body">"""}'
                    f'You could operate as a private limited UK company, an overseas branch of your existing '
                    f"company, or perhaps a joint venture with a UK business. You'll need to choose before "
                    f'registering.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'You must register your company with Companies House, the government organisation '
                    f'responsible for registration of companies in the UK, if you want to set up a place of '
                    f'business in the UK.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<a class="govuk-link" href="/international/expand-your-business-in-the-uk/guide/'
                    f'detailed-guides/set-up-and-register-your-business">'
                    f'Read our guide on how to set up and register your business'
                    f'</a>'
                    f'</p>'
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
                    f'{"""<p class="govuk-body">"""}'
                    f'A visa application decision takes 3 weeks on average, if it does not involve '
                    f'endorsement or sponsorship.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'If an endorsement is needed, the process can take up to 7 weeks in total. If '
                    f'sponsorship is needed, this process plus the visa application can take around 11 '
                    f'weeks in total.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'You may or may not need to apply for a visa, depending on your circumstances and '
                    f'planned business activities.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<a class="govuk-link" href="/international/expand-your-business-in-the-uk/guide/'
                    f'detailed-guides/how-to-apply-for-a-visa">'
                    f'Read our guide on visa types'
                    f'</a>'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<a class="govuk-link" href="https://www.gov.uk/check-uk-visa">'
                    f'Check if you need a visa on GOV.UK'
                    f'</a>'
                    f'</p>'
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
                    f'{"""<p class="govuk-body">"""}'
                    f"You'll need a UK business bank account to trade in the UK. You can choose between "
                    f'traditional banks and digital-only banks.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'Digital-only banks can open accounts in hours or days, but may have limited services. '
                    f'Traditional banks take longer but offer a full range of business banking services.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<a class="govuk-link" href="/international/expand-your-business-in-the-uk/guide/'
                    f'detailed-guides/how-to-choose-and-set-up-a-uk-bank-account/">'
                    f'Read our guide on business banking'
                    f'</a>'
                    f'</p>'
                )
            },
        },
        {
            'heading': {'text': 'Register for tax and claim tax allowances'},
            'summary': {'text': "You'll need to set up to pay Corporation Tax and check for other tax obligations."},
            'content': {
                'html': (
                    f'{"""<p class="govuk-body">"""}'
                    f'<span class="govuk-!-font-weight-bold">Corporation Tax</span>'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'If your business is based in the UK, you must pay Corporation Tax on all '
                    f'profits from the UK and abroad.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f"If your business isn't based in the UK but has an office or branch here, "
                    f'you will only pay Corporation Tax on profits from UK activities.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f"You'll need to register to pay tax within 3 months of starting to do business. "
                    f'This includes buying, selling, advertising, renting a property and employing someone.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<span class="govuk-!-font-weight-bold">Value Added Tax</span>'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f"You must register for Value Added Tax (VAT) with HMRC if your business' "
                    f"taxable turnover is more than £85,000. You'll need to do this within "
                    f'30 days of the end of the month when you went over this amount.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<a class="govuk-link" href="/international/expand-your-business-in-the-uk/'
                    f'guide/detailed-guides/how-to-register-for-tax-and-claim-tax-allowances">'
                    f'Read our guide on how to register for UK taxes and claim tax allowances'
                    f'</a>'
                    f'</p>'
                )
            },
        },
        {
            'heading': {'text': 'Know UK employment regulations'},
            'summary': {'text': "You'll need to be aware of UK employment law and your duties as a UK employer."},
            'content': {
                'html': (
                    f'{"""<p class="govuk-body">"""}'
                    f'<a class="govuk-link" '
                    f'href="/international/expand-your-business-in-the-uk/guide/detailed-guides/'
                    f'know-uk-employment-regulations">'
                    f'Read our guide on how to employ people in the UK'
                    f'</a>'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'You need a sponsor licence, valid for 4 years, to hire most eligible employees '
                    f'from outside the UK.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<a class="govuk-link" href="https://www.gov.uk/apply-sponsor-licence" target="_blank">'
                    f'Apply for a sponsor licence on GOV.UK'
                    f'</a>'
                    f'</p>'
                )
            },
        },
        {
            'heading': {'text': 'Register as an employer'},
            'summary': {'text': 'Setting up a payroll with HM Revenue and Customs can take up to 3 weeks.'},
            'content': {
                'html': (
                    f'{"""<p class="govuk-body">"""}'
                    f'This is the amount of time it can take to receive an employer Pay '
                    f'As You Earn (PAYE) reference number.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'As an employer, you usually have to set up PAYE as part of your payroll. '
                    f'This system collects Income Tax and National Insurance via UK employers.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'You must register before your first business payday.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<a class="govuk-link" href="https://www.gov.uk/register-employer" target="_blank">'
                    f'Register as an employer with HM Revenue and Customs on GOV.UK'
                    f'</a>'
                    f'</p>'
                )
            },
        },
        {
            'heading': {'text': 'Recruit and develop expert talent'},
            'summary': {
                'text': "There's a range of resources available to help you recruit or "
                'train the right people. '
                '1 to 4 months to buy one.'
            },
            'content': {
                'html': (
                    f'{"""<p class="govuk-body">"""}'
                    f'From advertising jobs to accessing government skills programmes, '
                    f'see our <a class="govuk-link" href="/international/'
                    f'expand-your-business-in-the-uk/guide/detailed-guides/find-expert-talent">'
                    f'guide on recruiting expert talent'
                    f'</a>'
                    f'</p>'
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
                    f'{"""<p class="govuk-body">"""}'
                    f'A suitable location near to customers, staff and supply chains, is important to your '
                    f'success in the UK.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'You can find a range of premises to suit your business including leased offices, '
                    f'co-working spaces and science parks.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<a class="govuk-link" href="/international/expand-your-business-in-the-uk/guide/'
                    f'detailed-guides/find-the-right-location-and-premises">'
                    f'Read our guide on how to find the right business property'
                    f'</a>'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<a class="govuk-link" href="https://www.great.gov.uk/international/'
                    f'investment/regions/" target="_blank">'
                    f"Learn more about the UK's nations and regions"
                    f'</a>'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<a class="govuk-link" href="https://www.great.gov.uk/international/'
                    f'investment-support-directory" target="_blank">'
                    f'Find professional help to locate in the UK'
                    f'</a>'
                    f'</p>'
                )
            },
        },
        {
            'heading': {'text': 'Get business insurance'},
            'summary': {'text': "You'll need to obtain cover for various parts of your business."},
            'content': {
                'html': (
                    f'{"""<p class="govuk-body">"""}'
                    f"You must get Employers' Liability insurance as soon as you become an employer. UK "
                    f'law also requires you to have third party motor insurance if you use a vehicle for '
                    f'business purposes.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'Other things which might have to be insured includes assets, income, liabilities '
                    f'and people.'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<a class="govuk-link" href="https://www.gov.uk/employers-liability-insurance" '
                    f'target="_blank">'
                    f"Employers' Liability Insurance on GOV.UK"
                    f'</a>'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'<a class="govuk-link" href="https://www.great.gov.uk/international/'
                    f'investment-support-directory" target="_blank">'
                    f'Find professional advice on business insurance'
                    f'</a>'
                    f'</p>'
                    f'<p class="govuk-body">'
                    f'It can take around 2 weeks to 1 month to arrange business insurance.'
                    f'</p>'
                )
            },
        },
    ]

    return {'items': items, 'id': 'accordion-default', 'classes': ''}
