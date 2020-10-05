from great_components import forms
from django.forms import ImageField, Textarea, NumberInput, Select

import directory_validators.url
import directory_validators.string
import directory_validators.file
from directory_constants.choices import TURNOVER_CHOICES

from core.helpers import population_age_range_choices


class LogoForm(forms.Form):
    logo = ImageField(
        help_text=(
            'For best results this should be a transparent PNG file of 600 x '
            '600 pixels and no more than 2MB',
        ),
        required=True,
        validators=[directory_validators.file.logo_filesize, directory_validators.file.image_format]
    )


class CountryDemographicsForm(forms.Form):
    COUNTRY_CHOICES = [
        'Australia',
        'Brazil',
        'China',
        'France',
        'Germany',
        'India',
        'United States',
    ]

    name = forms.ChoiceField(
        label='Country name',
        choices=((i, i) for i in COUNTRY_CHOICES)
    )
    age_range = forms.ChoiceField(
        choices=((i, i) for i in population_age_range_choices)
    )


class ExportPlanAboutYourBusinessForm(forms.Form):
    story = forms.CharField(
        label='How we started',
        required=False,
        widget=Textarea(attrs={
            'example': (
                'Dove Gin was founded in 2012 when Simon Dove started to distill gin in his garage in '
                'Shrewsbury. Simon came across a book of gin recipes on a visit to The Gin Museum of '
                'London. This inspired him to recreate gin distilled in the midlands 200 hundred years '
                'ago, with a modern twist.'
            ),
            'tooltip': (
                'It’s best to stick to the facts and keep things simple for each bit of text you add '
                'to your plan.'
            )}
        ),
    )
    location = forms.CharField(
        label="Where we're based",
        required=False,
        widget=Textarea(attrs={
            'example': (
                'By 2015 the garage was too small for the volumes we produced so we moved to larger '
                'premises in rented, shared business space in Shrewsbury.'
            )}
        ),
    )
    processes = forms.CharField(
        label='How we make our products',
        required=False,
        widget=Textarea(attrs={
            'example': (
                'We use vacuum distillation instead of traditional pot distillation. This  preserves '
                'the richness of flavour and aromas of the botanicals that give our gin its purity of '
                'taste.'
            )}
        ),
    )
    packaging = forms.CharField(
        label='Our packaging',
        required=False,
        widget=Textarea(attrs={
            'example': (
                'Our packaging is themed around purity and comprises elegant clear glass bottles with '
                'twist cap and unbleached paper label printed with natural dyes. Our distribution and '
                'delivery boxes are 100% recycled cardboard. Each features our distinctive Dove label. '
            )}
        ),
    )
    performance = forms.ChoiceField(
        label='Business performance',
        choices=TURNOVER_CHOICES,
        required=False,
        widget=Select(attrs={
            'example': (
                'From 2015 to 2018 sales have grown on average 31% a year. Revenue flattened off '
                'slightly in 2019 because of a UK distribution issue which has now been resolved. '
                'We are on track to meet our sales targets for 2020.'
            ),
            'tooltip': (
                'Give a summary of the past 3 to 5 years. You could include sales and profit figures '
                'or percentages, together with a brief description of any significant events.'
            ),
        }
        ),
    )


class ExportPlanAdaptationForTargetMarketForm(forms.Form):
    labelling = forms.CharField(
        label='Labelling',
        required=False,
        widget=Textarea(attrs={
            'tooltip': (
                'Labelling is used to inform the consumer about the product you are selling to them. '
                'Labelling will need to be changed to fit into the market you are selling to. For example '
                'some pictures and colours may not be appropriate for certain markets. You will have to '
                'research what the requirements are so your products have the correct labels for your '
                'target market.'
            ),
            'placeholder': (
                'Describe alterations'
            )}
        ),
    )
    packaging = forms.CharField(
        label='Packaging',
        required=False,
        widget=Textarea(attrs={
            'tooltip': (
                'Packaging provides protection for your product and prepares your product to be safely stored '
                'and transported. The information you need to include on your packaging will change depending '
                'on the market.You will have to research packaging requirements for your target market to avoid '
                'your products becoming damaged, lost or rejected.'
            ),
            'placeholder': (
                'Describe alterations'
            )}
        ),
    )
    size = forms.CharField(
        label='Size',
        required=False,
        widget=Textarea(attrs={
            'tooltip': (
                'Standard product sizes vary by country depending on factors like buying habits in each '
                'market. Consumers who buy less may want larger products to last them longer between '
                'shopping trips. You will have to research the size of products sold in this market so '
                'you meet customer needs for your target market.'
            ),
            'placeholder': (
                'Describe alterations'
            )}
        ),
    )
    standards = forms.CharField(
        label='Product changes to comply with standards',
        required=False,
        widget=Textarea(attrs={
            'tooltip': (
                'Your product will have to comply with local standards, if it does not comply it will not '
                'be allowed to be sold. For example you may have to change the voltage of electrical products '
                'in order to comply with safety regulations in that market. You will have to research '
                'standards relevant to your product to make sure they are compliant.'
            ),
            'placeholder': (
                'Describe alterations'
            )}
        ),
    )
    translations = forms.CharField(
        label='Translations',
        required=False,
        widget=Textarea(attrs={
            'tooltip': (
                'Translations'
            ),
            'placeholder': (
                'Describe alterations'
            )}
        ),
    )
    other_changes = forms.CharField(
        label='Other changes',
        required=False,
        widget=Textarea(attrs={
            'tooltip': (
                'Other changes'
            ),
            'placeholder': (
                'Describe alterations'
            )}
        ),
    )


class ExportPlanTargetMarketsResearchForm(forms.Form):
    demand = forms.CharField(
        label='Describe the consumer demand for your product in the Netherlands',
        required=False,
        widget=Textarea(attrs={
            'example': (
                '<p>Gin imports are hugely on the rise in Australia. The market was worth over 60 '
                'million USD in 2019, a massive increase of 25% year on year. This is predicted '
                'to continue growing at 9%.</p> <p>Meanwhile, UK gin imports were worth 12 million USD '
                'in 2019. This is a market that’s thirsty for gin and very open to new products. '
                'In the past 5 years over 75 new distilleries have opened.</p> <p>Our target age group, '
                '25-54 year olds, makes up 40% of the population. The average income is also '
                'increasing - currently 45,000 USD, up 3% compared to 2019.</p> <p>Australia is also '
                'a straightforward export market despite its distance. There are no trade '
                'barriers, they speak the same language and have similar tastes in other beverages '
                'such as beer and wine.</p>'
            ),
            'description': (
                'Demand for your product will be shaped by factors such as a country’s economy and '
                'population. Make sure you include any useful figures as these will underpin your '
                'understanding of the market.'
            )}
        ),
    )
    competitors = forms.CharField(
        label='Who are your competitors in the Netherlands?',
        required=False,
        widget=Textarea(attrs={
            'example': (
                '<ul><li>Poor Tom’s Gin</li> <li>The Melbourne Gin Company - main local competitor</li>'
                '<li>Butlers Gin (UK)</li> <li>Plymouth Gin (UK) - main British export competitor</li></ul>'
            ),
            'description': (
                'Consider including businesses that sell similar products, as well as the other brands '
                'or companies operating in the country.'
            )}
        ),
    )
    trend = forms.CharField(
        label='What are the product trends in the Netherlands?',
        required=False,
        widget=Textarea(attrs={
            'example': (
                '<p>There are already over 100 craft gin distilleries in Australia. The main trend seems '
                'to be using native Australian ingredients to create a modern twist on traditional gin '
                'flavours.</p> <p>The market is fairly similar to the UK in terms of consumption and age. Gin '
                'bars are on the increase in the main cities. Online gin clubs that offer monthly gin '
                'subscriptions to their members are also popular.</p>'
            ),
            'description': (
                'Describe what you know about the product market in the Netherlands. What’s popular right '
                'now? Are there new products on the market? Where do people buy it?'
            )}
        ),
    )
    unqiue_selling_proposition = forms.CharField(
        label='What’s your unique selling proposition for the Netherlands?',
        required=False,
        widget=Textarea(attrs={
            'example': (
                'Dove Gin’s historic backstory is definitely appealing and will make us stand out from '
                'the competition. We also know our product design is very appealing and unique.'
            ),
            'description': (
                'Explain your product’s particular appeal to consumers in the Netherlands. Why would they '
                'buy it rather than another brand?'
            )}
        ),
    )
    average_price = forms.CharField(
        label='What’s the avg price for your product in the Netherlands?',
        required=False,
        widget=NumberInput(attrs={
            'placeholder': (
                0.00
            ),
            'currency': (
                'GBP'
            )},
        ),
    )


class ExportPlanBusinessObjectivesForm(forms.Form):
    rationale = forms.CharField(
        label='Why you want to export',
        required=False,
        widget=Textarea(attrs={
            'placeholder': 'Add some text',
            'description': (
                '<p>What are the main reasons you want to export?</p><p>Common reasons for exporting include:</p>'
                '<ul class="list-dot"><li>grow the business by selling overseas</li><li>maintain growth when sales'
                ' in the UK have levelled off</li><li>spread risk evenly by selling in countries other than the '
                'UK</li><li>widen your customer base</li></ul> <p class="g-panel">Planning and thinking about your'
                ' export objectives will help you make the most out of any export opportunities you are interested'
                ' in.</p>'
            ),
            'example': (
                'A desire for taste lacking in big brands is creating a buzz around "craft" gin distilleries '
                ' - especially those in the UK. Dove gin is what we anticipate is long term growth in major '
                'cities in Europe, Asia and the US.'

            ),
        })
    )


class ExportPlanMarketingApproachForm(forms.Form):

    resources = forms.CharField(
        label='What marketing resources do you need?',
        required=False,
        widget=Textarea(attrs={
            'example': (
                '<p>Right now it’s not practical for the team to travel to Australia, so we’re '
                'aiming to establish Dove Gin by creating a buzz from the UK.</p><p>Our research '
                'shows that the Australian gin market is similar to the UK. However as a niche '
                'British product (rather than local hero), we’ll have to adapt the current Dove '
                'Gin marketing strategy.</p><p>There are already over 100 craft gin distilleries '
                'in Australia, so we’re focused on what makes Dove Gin unique.</p><p>We’re '
                'capitalising on our historic recipe backstory to make us stand out from the '
                'competition. We also know our product design is very appealing - and tastes as '
                'good as it looks.</p><p>We’ll be working with our existing marketing agency Blue '
                'Sky to run paid social campaigns to raise awareness of our product in Australia.</p>'
                '<p>Our agency will also help with search engine optimisation so that Dove Gin appears '
                'in search results for craft gin in Australia. We’re very active on our brand social '
                'media accounts. We’re building up our connections with Australian influencers - bar '
                'owners, gin bloggers and premium gin importers. Once we have an Australian distributor,'
                'we’ll be able to leverage their promotional channels to reach a wider audience, for '
                'example liquor store email marketing campaigns.</p>'
            ),
            'description': (
                '<p>Write down:</p><ul class="list-bullet"><li>what marketing you can do in-house</li>'
                '<li>the areas where your business will need support</li><li>external agencies or '
                'people you’ll work with and what you expect them to do</li>'
            )}
        ),
    )
    spending = forms.CharField(
        label='How much do you think you’ll spend on marketing?',
        required=False,
        widget=NumberInput(attrs={
            'example': (
                '<p>We think we’ll spend around £13,000 a year in 2021 and 2022 on marketing for Dove Gin’s '
                'launch in Australia.</p><p>The main costs will be:</p><ul><li>£500 per month for paid search '
                'for a 6 month campaign late 2021</li><li>£5,000 agency fees</li></ul><p>Remaining budget tbc '
                'but will need to include giveaways and potential cost of sponsoring launch nights at bars in '
                'late 2021.</p>'
            ),
            'description': (
                '<p>Explain how your total marketing spend breaks down.</p>'
            ),
            'placeholder': (
                0.00
            ),
            'currency': (
                'GBP'
            )},
        ),
    )
