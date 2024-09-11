import directory_validators.file
from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ChoiceField,
    ImageField,
    MultipleChoiceField,
    NumberInput,
    RadioSelect,
    Textarea,
    TextInput,
)
from great_components import forms

from core import constants
from core.validators import validate_file_infection


class LogoForm(forms.Form):
    logo = ImageField(
        help_text=('For best results this should be a transparent PNG file of 600 x 600 pixels and no more than 2MB',),
        required=True,
        validators=[
            directory_validators.file.logo_filesize,
            directory_validators.file.image_format,
            validate_file_infection,
        ],
    )


class ExportPlanAdaptingYourProductForm(forms.Form):
    labelling = forms.CharField(
        label='Labelling',
        required=False,
        widget=Textarea(
            attrs={
                'tooltip': (
                    'Labelling is used to inform the consumer about the product you are selling to them. '
                    'Labelling will need to be changed to fit into the market you are selling to. For example '
                    'some pictures and colours may not be appropriate for certain markets. You will have to '
                    'research what the requirements are so your products have the correct labels for your '
                    'target market.'
                ),
                'placeholder': 'Describe alterations',
            }
        ),
    )
    packaging = forms.CharField(
        label='Packaging',
        required=False,
        widget=Textarea(
            attrs={
                'tooltip': (
                    'Packaging provides protection for your product and prepares your product to be safely stored '
                    'and transported. The information you need to include on your packaging will change depending '
                    'on the market.You will have to research packaging requirements for your target market to avoid '
                    'your products becoming damaged, lost or rejected.'
                ),
                'placeholder': 'Describe alterations',
            }
        ),
    )
    size = forms.CharField(
        label='Size',
        required=False,
        widget=Textarea(
            attrs={
                'tooltip': (
                    'Standard product sizes vary by country depending on factors like buying habits in each '
                    'market. Consumers who buy less may want larger products to last them longer between '
                    'shopping trips. You will have to research the size of products sold in this market so '
                    'you meet customer needs for your target market.'
                ),
                'placeholder': 'Describe alterations',
            }
        ),
    )
    standards = forms.CharField(
        label='Product changes to comply with standards',
        required=False,
        widget=Textarea(
            attrs={
                'tooltip': (
                    'Your product will have to comply with local standards, if it does not comply it will not '
                    'be allowed to be sold. For example you may have to change the voltage of electrical products '
                    'in order to comply with safety regulations in that market. You will have to research '
                    'standards relevant to your product to make sure they are compliant.'
                ),
                'placeholder': 'Describe alterations',
            }
        ),
    )
    translations = forms.CharField(
        label='Translations',
        required=False,
        widget=Textarea(attrs={'tooltip': 'Translations', 'placeholder': 'Describe alterations'}),
    )
    other_changes = forms.CharField(
        label='Other changes',
        required=False,
        widget=Textarea(attrs={'tooltip': 'Other changes', 'placeholder': 'Describe alterations'}),
    )
    certificate_of_origin = forms.CharField(
        label='Certificate of origin',
        required=False,
        widget=Textarea(attrs={'tooltip': 'Certificate of origin', 'placeholder': 'Add notes'}),
    )
    insurance_certificate = forms.CharField(
        label='Insurance certificate',
        required=False,
        widget=Textarea(attrs={'tooltip': 'Insurance certificate', 'placeholder': 'Add note'}),
    )
    commercial_invoice = forms.CharField(
        label='Commercial invoice',
        required=False,
        widget=Textarea(attrs={'tooltip': 'Commercial invoice', 'placeholder': 'Add note'}),
    )
    uk_customs_declaration = forms.CharField(
        label='UK customs declaration',
        required=False,
        widget=Textarea(attrs={'tooltip': 'UK customs declaration', 'placeholder': 'Add note'}),
    )


class ExportPlanTargetMarketsResearchForm(forms.Form):
    def __init__(self, country_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if country_name:
            self.set_country_specific_text(country_name)

    def set_country_specific_text(self, country_name):
        self.country_name = country_name
        self.fields['demand'].label = f'Describe the consumer demand for your product in the {country_name}'
        self.fields['competitors'].label = f'Who are your competitors in the {country_name}?'
        self.fields['trend'].label = f'What are the product trends in the {country_name}?'
        self.fields['unqiue_selling_proposition'].label = (
            f'What’s your unique selling proposition for the {country_name}?'
        )
        self.fields['average_price'].label = f'What’s the avg price for your product in the {country_name}?'
        self.fields['trend'].widget.attrs['description'] = (
            f'Describe what you know about the product market in the {country_name}. '
            'What’s popular right now? Are there new products on the market? Where do people buy it?'
        )
        self.fields['unqiue_selling_proposition'].widget.attrs['description'] = (
            f'Explain your product’s particular appeal to consumers in the {country_name}. '
            'Why would they buy it rather than another brand?'
        )

    demand = forms.CharField(
        required=False,
        widget=Textarea(
            attrs={
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
                ),
            }
        ),
    )

    competitors = forms.CharField(
        required=False,
        widget=Textarea(
            attrs={
                'example': (
                    '<ul><li>Poor Tom’s Gin</li> <li>The Melbourne Gin Company - main local competitor</li>'
                    '<li>Butlers Gin (UK)</li> <li>Plymouth Gin (UK) - main British export competitor</li></ul>'
                ),
                'description': (
                    'Consider including businesses that sell similar products, as well as the other brands '
                    'or companies operating in the country.'
                ),
            }
        ),
    )
    trend = forms.CharField(
        required=False,
        widget=Textarea(
            attrs={
                'example': (
                    '<p>There are already over 100 craft gin distilleries in Australia. The main trend seems '
                    'to be using native Australian ingredients to create a modern twist on traditional gin '
                    'flavours.</p> <p>The market is fairly similar to the UK in terms of consumption and age. Gin '
                    'bars are on the increase in the main cities. Online gin clubs that offer monthly gin '
                    'subscriptions to their members are also popular.</p>'
                )
            }
        ),
    )
    unqiue_selling_proposition = forms.CharField(
        required=False,
        widget=Textarea(
            attrs={
                'example': (
                    'Dove Gin’s historic backstory is definitely appealing and will make us stand out from the '
                    'competition. We also know our product design is unusual.'
                ),
            }
        ),
    )
    average_price = forms.CharField(
        required=False,
        widget=NumberInput(
            attrs={'placeholder': '0.00', 'currency': 'GBP'},
        ),
    )


class ExportPlanMarketingApproachForm(forms.Form):
    resources = forms.CharField(
        label='What marketing resources do you need?',
        required=False,
        widget=Textarea(
            attrs={
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
                    '<p class="m-0">To make sure you have the right amount of marketing resources write down:</p>'
                    '<ul class="list-dot"><li>what marketing you can do in-house</li>'
                    '<li>the areas where your business will need support</li><li>external agencies or '
                    'people you will work with and what they will be doing</li>'
                ),
            }
        ),
    )


class CsatUserFeedbackForm(forms.Form):
    satisfaction = ChoiceField(
        label='Overall, how would you rate your experience with the Where to export service today?',
        choices=constants.SATISFACTION_CHOICES,
        widget=RadioSelect(attrs={'class': 'govuk-radios__input'}),
        required=False,
    )
    experience = MultipleChoiceField(
        label='Did you experience any of the following issues?',
        help_text='Select all that apply.',
        choices=constants.EXPERIENCE_CHOICES,
        widget=CheckboxSelectMultiple(attrs={'class': 'govuk-checkboxes__input'}),
        required=False,
        error_messages={
            'required': "Select issues you experienced, or select 'I did not experience any issues'",
        },
    )
    experience_other = CharField(
        label='Please describe the issue',
        min_length=2,
        max_length=255,
        required=False,
        widget=TextInput(attrs={'class': 'govuk-input great-font-main'}),
    )
    feedback_text = CharField(
        label='How could we improve this service?',
        help_text="Don't include any personal information, like your name or email address.",
        max_length=1200,
        required=False,
        error_messages={'max_length': 'Your feedback must be 1200 characters or less'},
        widget=Textarea(
            attrs={
                'class': 'govuk-textarea govuk-js-character-count great-font-main',
                'rows': 6,
                'id': 'id_feedback_text',
                'name': 'withHint',
                'aria-describedby': 'id_feedback_text-info id_feedback_text-hint',
            }
        ),
    )
    likelihood_of_return = ChoiceField(
        label='How likely are you to use this service again?',
        choices=constants.LIKELIHOOD_CHOICES,
        widget=RadioSelect(attrs={'class': 'govuk-radios__input'}),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        experience = cleaned_data.get('experience')

        if experience and 'OTHER' not in experience:
            cleaned_data['experience_other'] = ''

        if experience and any('NO_ISSUE' in s for s in experience):
            for option in experience:
                if option != 'NO_ISSUE':
                    self.add_error(
                        'experience', "Select issues you experienced, or select 'I did not experience any issues'"
                    )
                    break
        return cleaned_data
