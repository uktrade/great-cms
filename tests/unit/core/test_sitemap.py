import datetime

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse
from django.utils.timezone import now as tz_now

from config import settings
from tests.unit.core import factories as core_factories
from tests.unit.domestic import factories as domestic_factories

pytestmark = pytest.mark.django_db


def test_sitemaps(
    client,
    domestic_site,
):
    url = reverse('core:sitemap')
    response = client.get(url)
    assert response.status_code == 200


def test_sitemap_includes_expected_django_pages(
    client,
    domestic_site,
):
    expected_django_paths = [
        '/get-finance/',
        '/get-finance/contact/',
        '/project-finance/',
        '/how-we-assess-your-project/',
        '/what-we-offer-you/',
        '/country-cover/',
        '/uk-export-contact-form/',
        '/report-trade-barrier/',
        '/report-trade-barrier/report/about/',
        '/search/',
        '/search/feedback/',
        '/contact/',
        '/contact/events/',
        '/contact/defence-and-security-organisation/',
        '/contact/export-advice/',
        '/contact/feedback/',
        '/contact/domestic/',
        '/contact/domestic/enquiries/',
        '/contact/international/',
        '/robots.txt',
    ]

    unexpected_django_path_prefixes = [
        '/api/',  # ANYTHING with /api/ in it
        '/admin/',
        '/django-admin/',
        '/documents/',
        '/great-cms-sso/',
        '/export-plan/',
        '/activity-stream/',
        '/contact-us/',  # depecated MVP contact pages
        '/signup/company-name/',
        '/signup/tailored-content/',
        '/signup/export-plan/',
        '/custom/',
        '/triage/',
        '/healthcheck/',
        '/sitemap.xml',
        '/capability/',
        # These were removed from the V1 sitemap because the pages were 404ing anyway because
        # FEATURE_EXPORTING_TO_UK_ON_ENABLED was not set on production any more, so the views
        # ExportingToUKDERAFormView, ExportingToUKBEISFormView and ExportingToUKFormView have
        # NOT YET been ported to Great V2
        '/contact/exporting-to-the-uk/',
        '/contact/exporting-to-the-uk/import-controls/',
        '/contact/exporting-to-the-uk/other/',
        '/contact/exporting-to-the-uk/trade-with-uk-app/',
        '/contact/department-for-business-energy-and-industrial-strategy/',
        '/contact/department-for-environment-food-and-rural-affairs/',
    ]

    url = reverse('core:sitemap')
    response = client.get(url)
    sitemap_soup = BeautifulSoup(response.content)

    locs = [x.text for x in sitemap_soup.find_all('loc')]

    for path_ in expected_django_paths:
        assert f'http://testserver{path_}' in locs

    for path_ in unexpected_django_path_prefixes:
        assert f'http://testserver{path_}' not in locs


def test_sitemap_excludes_wagtail_pages_that_require_auth(  # noqa: C901
    client,
    domestic_site,
    domestic_homepage,
):
    dashboard = domestic_factories.DomesticDashboardFactory(
        parent=domestic_homepage,
        slug='dashboard',
    )
    landing_page = core_factories.LandingPageFactory(
        parent=domestic_homepage,
        slug='landing-page',
    )
    list_page = core_factories.ListPageFactory(
        parent=dashboard,
        record_read_progress=False,
        slug='list-page',
    )
    module_page = core_factories.CuratedListPageFactory(
        parent=list_page,
        slug='module-page',
    )
    topic_page = core_factories.TopicPageFactory(
        parent=module_page,
        slug='topic-page',
    )
    lesson_page_1 = core_factories.DetailPageFactory(
        parent=topic_page,
        slug='lesson-page-1',
    )
    lesson_page_1.live = False
    lesson_page_1.save()
    lesson_page_2 = core_factories.DetailPageFactory(
        parent=topic_page,
        slug='lesson-page-2',
    )
    advice_topic_page = domestic_factories.TopicLandingPageFactory(
        title='Advice',
        parent=domestic_homepage,
        slug='advice',
    )
    article_list_one = domestic_factories.ArticleListingPage(
        title='list one',
        landing_page_title='List One',
        slug='article-list-1',
    )
    article_list_two = domestic_factories.ArticleListingPage(
        title='list two',
        landing_page_title='List Two',
        slug='article-list-2',
    )
    article_list_three = domestic_factories.ArticleListingPage(
        title='list three',
        landing_page_title='List Three',
        slug='article-list-3',
    )

    # note deliberate out-of-sequence ordering here
    advice_topic_page.add_child(instance=article_list_two)
    advice_topic_page.add_child(instance=article_list_one)
    advice_topic_page.add_child(instance=article_list_three)

    article_list_three.live = False
    article_list_three.save()

    for i in range(5):
        _title = f'Article A{i}'
        domestic_factories.ArticlePageFactory(
            title=_title,
            article_title=_title,
            parent=article_list_one,
        )
    # make one of them not live
    x = domestic_factories.ArticlePage.objects.get(title='Article A3')
    x.live = False
    x.save()

    for i in range(3):
        _title = f'Article B{i}'
        domestic_factories.ArticlePageFactory(
            title=_title,
            article_title=_title,
            parent=article_list_two,
        )

    # make one of them not live
    x = domestic_factories.ArticlePage.objects.get(title='Article B0')
    x.live = False
    x.save()

    for i in range(4):
        _title = f'Article C{i}'
        domestic_factories.ArticlePageFactory(
            title=_title,
            article_title=_title,
            parent=article_list_three,
        )

    for i in range(2):
        _title = f'Article D{i}'
        domestic_factories.ArticlePageFactory(
            title=_title,
            article_title=_title,
            parent=advice_topic_page,
        )

    # make one of them not live
    x = domestic_factories.ArticlePage.objects.get(title='Article D0')
    x.live = False
    x.save()

    markets_page = domestic_factories.MarketsTopicLandingPageFactory(
        parent=domestic_homepage,
        slug='markets',
        title='Markets',
    )

    _now = tz_now()
    for i in range(10):
        domestic_factories.CountryGuidePageFactory(
            parent=markets_page,
            title=f'Test GCP {i}',
            slug=f'market-guide-{i}',
            live=True,
            last_published_at=_now - datetime.timedelta(minutes=i),
        )
    # make one of them not live
    x = domestic_factories.CountryGuidePage.objects.get(slug='market-guide-9')
    x.live = False
    x.save()

    services_page = domestic_factories.ManuallyConfigurableTopicLandingPageFactory(
        parent=domestic_homepage,
        title='Services',
        slug='services',
    )

    url = reverse('core:sitemap')
    response = client.get(url)
    sitemap_soup = BeautifulSoup(response.content, features='xml')

    locs = [x.text for x in sitemap_soup.find_all('loc')]

    expected_in_map = [
        domestic_homepage.url,
        article_list_one.url,
        article_list_two.url,
        '/advice/article-list-1/article-a0/',
        '/advice/article-list-1/article-a1/',
        '/advice/article-list-1/article-a2/',
        '/advice/article-list-2/article-b1/',
        '/advice/article-list-2/article-b2/',
        '/advice/article-list-2/article-b1/',
        '/advice/article-list-3/article-c0/',  # even though /advice/article-list-3/ is not live
        '/advice/article-list-3/article-c1/',  # even though /advice/article-list-3/ is not live
        '/advice/article-list-3/article-c2/',  # even though /advice/article-list-3/ is not live
        '/advice/article-list-3/article-c3/',  # even though /advice/article-list-3/ is not live
        '/advice/article-d1/',
        '/markets/',
        '/markets/market-guide-0/',
        '/markets/market-guide-1/',
        '/markets/market-guide-2/',
        '/markets/market-guide-3/',
        '/markets/market-guide-4/',
        '/markets/market-guide-5/',
        '/markets/market-guide-6/',
        '/markets/market-guide-7/',
        '/markets/market-guide-8/',
        services_page.url,
    ]

    not_expected_in_map = [
        dashboard.url,  # needs auth
        lesson_page_1.url,  # needs auth AND draft
        article_list_three.url,  # draft/not live
        '/advice/article-list-1/article-a3/',  # draft/not live
        '/advice/article-d0/',  # draft/not live
        '/markets/market-guide-9/',  # draft/not live
    ]

    if settings.FEATURE_DEA_V2:
        expected_in_map.append(landing_page.url)  # does not needs auth
        expected_in_map.append(list_page.url)
        expected_in_map.append(module_page.url)
        expected_in_map.append(topic_page.url)
        expected_in_map.append(lesson_page_2.url)
    else:
        not_expected_in_map.append(landing_page.url)  # needs auth
        not_expected_in_map.append(list_page.url)
        not_expected_in_map.append(module_page.url)
        not_expected_in_map.append(topic_page.url)
        not_expected_in_map.append(lesson_page_2.url)
    # The CMS pages have a port in their test hostname, and the most reliable way to get
    # hold if it is simply to get it from the sitemap, dropping its trailing slash
    testserver_host = locs[0][:-1]
    for path_ in expected_in_map:
        expected = f'{testserver_host}{path_}'
        assert expected in locs

    for path_ in not_expected_in_map:
        not_expected = f'{testserver_host}{path_}'
        assert not_expected not in locs
