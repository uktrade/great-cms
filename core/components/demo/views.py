import ast
import re
import lorem

from unittest.mock import Mock
from collections import namedtuple

from django.core.paginator import Paginator
from django.shortcuts import Http404
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.utils.text import slugify
from django.contrib.staticfiles.templatetags.staticfiles import static

from directory_components.mixins import (
    CountryDisplayMixin, EnableTranslationsMixin
)

from demo import forms


class BasePageView(TemplateView):

    @property
    def template_name(self):
        return self.kwargs.get('template_name')


class KeyFactsView(BasePageView):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        key_facts = [
            {
                'icon': {
                    'url': static('images/icon1.png')
                },
                'heading': 'Heading 1',
                'content': (
                    '<p>Bacon ipsum dolor amet pork jerky sausage buffalo '
                    'chicken cow strip steak doner pancetta shoulder kielbasa rump ham.</p>'
                ),
            },
            {
                'icon': {
                    'url': static('images/icon2.png')
                },
                'heading': 'Heading 2',
                'content': (
                    '<p>Lorem ipsum dolor sit amet.</p>'
                    '<p><a class="link" href="/">Bacon ipsum dolor amet pork jerky sausage buffalo '
                    'chicken cow strip steak doner pancetta shoulder kielbasa rump ham</a></p>'
                    '<p><a class="link" href="/">Another link</a></p>'
                ),
            },
            {
                'icon': {
                    'url': static('images/icon3.png')
                },
                'heading': 'Heading 3',
                'content': (
                    '<p><a class="link" href="/">Yet more links</a></p>'
                    '<p><a class="link" href="/">So many links</a></p>'
                    '<p><a class="link" href="/">More links</a></p>'
                ),
            },
        ]
        context['key_facts'] = key_facts
        context['key_facts_two'] = key_facts[1:]
        context['key_facts_one'] = key_facts[:1]
        key_facts_no_icons = [
            {
                'heading': item['heading'],
                'content': item['content'],
            }
            for item in key_facts]
        context['key_facts_no_icons'] = key_facts_no_icons
        return context


class IndexPageView(BasePageView):
    def get_version(self):
        pattern = re.compile(r'version=(.*),')

        with open('setup.py', 'rb') as src:
            return str(ast.literal_eval(
                pattern.search(src.read().decode('utf-8')).group(1)
            ))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['version'] = self.get_version()
        return context


NavNode = namedtuple('NavItem', 'tier_one_item tier_two_items')


class TierOneNavItem:
    def __init__(self, title):
        self.title = title

    @property
    def name(self):
        return slugify(self.title)

    @property
    def url(self):
        return f'/great-international-header-footer/?section={self.name}'


class TierTwoNavItem:
    def __init__(self, title, parent_title):
        self.title = title
        self.parent_title = parent_title

    @property
    def parent_name(self):
        return slugify(self.parent_title)

    @property
    def name(self):
        return slugify(self.title)

    @property
    def url(self):
        return f'/great-international-header-footer/?section={self.parent_name}&sub_section={self.name}'


class InternationalHeaderView(CountryDisplayMixin, EnableTranslationsMixin, BasePageView):
    @property
    def header_section(self):
        return self.request.GET.get('section', '')

    @property
    def header_sub_section(self):
        return self.request.GET.get('sub_section', '')

    navigation_tree = [
        NavNode(
            tier_one_item=TierOneNavItem('About the UK'),
            tier_two_items=[
                TierTwoNavItem('Overview', 'About the UK'),
                TierTwoNavItem('Why choose the UK', 'About the UK'),
                TierTwoNavItem('Industries', 'About the UK'),
                TierTwoNavItem('Regions', 'About the UK'),
                TierTwoNavItem('Contact us', 'About the UK'),
            ]
        ),
        NavNode(
            tier_one_item=TierOneNavItem("Expand to the UK"),
            tier_two_items=[
                TierTwoNavItem('Overview', 'Expand to the UK'),
                TierTwoNavItem('How to expand to the UK', 'Expand to the UK'),
                TierTwoNavItem('Professional services', 'Expand to the UK'),
                TierTwoNavItem('Contact us', 'Expand to the UK'),
            ]
        ),
        NavNode(
            tier_one_item=TierOneNavItem("Invest capital in the UK"),
            tier_two_items=[
                TierTwoNavItem('Overview', 'Invest capital in the UK'),
                TierTwoNavItem('Investment types', 'Invest capital in the UK'),
                TierTwoNavItem('Investment Opportunities', 'Invest capital in the UK'),
                TierTwoNavItem('How to invest capital', 'Invest capital in the UK'),
                TierTwoNavItem('Contact us', 'Invest capital in the UK'),
            ]
        ),
        NavNode(
            tier_one_item=TierOneNavItem("Buy from the UK"),
            tier_two_items=[
                TierTwoNavItem('Buy from the UK', 'Buy from the UK'),
                TierTwoNavItem('Contact us', 'Buy from the UK'),
            ]
        ),
        NavNode(
            tier_one_item=TierOneNavItem("About us"),
            tier_two_items=[
                TierTwoNavItem('What we do', 'About us'),
                TierTwoNavItem('Contact us', 'About us'),
            ]
        ),
    ]

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            navigation_tree=self.navigation_tree,
            header_section=self.header_section,
            header_sub_section=self.header_sub_section,
            *args,
            **kwargs
        )


class InvestHeaderView(InternationalHeaderView):
    pass


class BreadcrumbsDemoPageView(BasePageView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['page'] = {
            'title': 'Breadcrumbs demo page',
            'url': '',
        }
        context['home_link'] = '/'
        context['home_label'] = 'Home'
        return context


class SearchPageComponentsDemoPageView(BasePageView):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(
            filters=['Energy', 'Real Estate', 'Automotive', 'Aerospace'],
            form=forms.MultipleChoiceForm(),
            *args, **kwargs
        )
        context['home_link'] = '/'
        context['home_label'] = 'Home'
        return context


class DemoStatsView(BasePageView):
    statistics = [
        {
            'heading': 'Ease of doing business',
            'number': '36',
            'smallprint': 'World Bank Ease of Doing Business ranking'
        },
        {
            'heading': 'Currency',
            'number': 'Euro',
            'smallprint': ''
        },
        {
            'heading': 'Business languages',
            'number': 'Dutch, English',
            'smallprint': ''
        },
        {
            'heading': 'GDP per capita',
            'number': '48,223.16 USD',
            'smallprint': 'UK GDP per capita is 39,800.3 USD'
        },
        {
            'heading': 'Economic growth',
            'number': '2.9%',
            'smallprint': 'in 2017'
        },
        {
            'heading': 'Time zone',
            'number': 'GMT+1',
            'smallprint': ''
        },
    ]
    num_of_statistics = 6


class DemoFormErrorsView(FormView):
    template_name = 'demo/form-errors.html'
    form_class = forms.DemoFormErrors
    success_url = reverse_lazy('form-errors')


class DemoFormView(TemplateView):
    template_name = 'demo/form-elements.html'

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            text_form=forms.TextBoxForm(),
            checkbox_form=forms.CheckboxForm(),
            multiple_choice_form=forms.MultipleChoiceForm(),
            radio_form=forms.RadioForm(),
            submit_button_form=forms.DemoFormWithSubmitButton(),
            nested_radio_form=forms.DemoNestedForm(),
            multiple_autocomplete_form=forms.MultiSelectAutoCompleteForm(),
            *args, **kwargs
        )


class Trigger404View(View):
    def dispatch(self, request):
        raise Http404()


class Trigger500ErrorView(View):
    def dispatch(self, request):
        raise Exception('triggering a server error')


class DemoPaginationView(TemplateView):
    template_name = 'demo/pagination.html'

    objects = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

    @property
    def pagination_few_pages(self):
        paginator = Paginator(self.objects, 10)
        return [paginator.page(index) for index in range(1, 3)]

    @property
    def pagination_some_pages(self):
        paginator = Paginator(self.objects, 3)
        return [paginator.page(index) for index in range(1, 6)]

    @property
    def pagination_many_pages(self):
        paginator = Paginator(self.objects, 1)
        return [paginator.page(index) for index in range(1, 16)]

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            pagination_page_few_pages=self.pagination_few_pages,
            pagination_page_some_pages=self.pagination_some_pages,
            pagination_page_many_pages=self.pagination_many_pages,
        )


class DomesticHeaderFooterView(TemplateView):
    template_name = 'demo/great-domestic-header-footer.html'

    def dispatch(self, request, *args, **kwargs):
        if 'authenticated' in request.GET:
            request.user = Mock(is_authenticated=True)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            sso_login_url='?authenticated',
            sso_logout_url='?unauthenticated',
        )


class FullWidthBannersView(TemplateView):
    template_name = 'demo/full-width-banners.html'

    def get_context_data(self, *args, **kwargs):
        return super().get_context_data(
            items_list=[
                {
                    'title': 'Item One Title',
                    'text': '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do. '
                            '<a href="/full-width-banners/">Learn more.</a></p>'
                },
                {
                    'title': 'Item Two Title',
                    'text': '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do. '
                            '<a href="/full-width-banners/">Learn more.</a></p>'
                },
                {
                    'title': 'Item Three Title',
                    'text': '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do. '
                            '<a href="/full-width-banners/">Learn more.</a></p>'
                },
                {
                    'title': 'Item Four Title',
                    'text': '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do. '
                            '<a href="/full-width-banners/">Learn more.</a></p>'
                }
            ],
            intro_markdown="<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                           "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>",
            video={
                'url': static('videos/hpo-food-video.mp4'),
                'file_extension': 'mp4'
            }
        )


class DetailsView(BasePageView):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        word = lorem.sentence().split(' ')[0]
        link = f'<p><a href="/foo">{word}</a></p>'
        list = f'<ul><li>{lorem.sentence()}</li><li>{lorem.sentence()}</li><li>{lorem.sentence()}</li></ul>'

        details_list = [
            {
                'heading': lorem.sentence(),
                'content': list + f'<p>{lorem.paragraph()}</p>'
            },
            {
                'heading': lorem.sentence(),
                'content': f'<p>{lorem.paragraph()}</p>' + link + link + f'<p>{lorem.paragraph()}</p>'
            },
            {
                'heading': lorem.sentence(),
                'content': f'<p>{lorem.paragraph()}</p>'
            },
        ]

        context['details_list'] = details_list
        return context


class FeaturedArticlesView(BasePageView):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        articles_list = [
            {
                'title': lorem.sentence(),
                'url': f'/{slugify(lorem.sentence())}',
                'type_of_article': 'Advice',
                'teaser': lorem.sentence(),
                'image': {
                    'url': static('images/card_image02.jpg'),
                },
                'image_alt': lorem.sentence(),
            },
            {
                'title': lorem.sentence(),
                'url': f'/{slugify(lorem.sentence())}',
                'type_of_article': 'Advice',
                'teaser': lorem.sentence(),
            },
            {
                'title': lorem.sentence(),
                'url': f'/{slugify(lorem.sentence())}',
                'type_of_article': 'Advice',
                'teaser': lorem.sentence(),
            },
            {
                'title': lorem.sentence(),
                'url': f'/{slugify(lorem.sentence())}',
                'type_of_article': 'Advice',
                'teaser': lorem.sentence(),
            },
            {
                'title': lorem.sentence(),
                'url': f'/{slugify(lorem.sentence())}',
                'type_of_article': 'Advice',
                'teaser': lorem.sentence(),
            },
            {
                'title': lorem.sentence(),
                'url': f'/{slugify(lorem.sentence())}',
                'type_of_article': 'Advice',
                'teaser': lorem.sentence(),
            },
        ]

        context['articles_list'] = articles_list
        return context
