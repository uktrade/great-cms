from demo import views
from django.conf.urls import url

urlpatterns = [
    url(
        r'^$',
        views.IndexPageView.as_view(),
        {'template_name': 'demo/index.html'},
        name='index',
    ),
    url(
        r'^404/$',
        views.Trigger404View.as_view(),
        name='404',
    ),
    url(
        r'^500/$',
        views.Trigger500ErrorView.as_view(),
        name='500',
    ),
    url(
        r'^great-domestic-header-footer/$',
        views.DomesticHeaderFooterView.as_view(),
        name='great-domestic-header-footer',
    ),
    url(
        r'^elements/$',
        views.BasePageView.as_view(),
        {'template_name': 'demo/elements.html'},
        name='elements',
    ),
    url(
        r'^details-accordions/$',
        views.DetailsView.as_view(),
        {'template_name': 'demo/details-accordions.html'},
        name='details-accordions',
    ),
    url(
        r'^key-facts/$',
        views.KeyFactsView.as_view(),
        {'template_name': 'demo/key-facts.html'},
        name='key-facts',
    ),
    url(
        r'^featured-articles/$',
        views.FeaturedArticlesView.as_view(),
        {'template_name': 'demo/featured-articles.html'},
        name='featured-articles',
    ),
    url(
        r'^statistics/$',
        views.DemoStatsView.as_view(),
        {'template_name': 'demo/statistics.html'},
        name='statistics',
    ),
    url(
        r'^widgets/$',
        views.DemoFormView.as_view(),
        name='widgets',
    ),
    url(
        r'^form-errors/$',
        views.DemoFormErrorsView.as_view(),
        name='form-errors',
    ),
    url(
        r'^components/$',
        views.BasePageView.as_view(),
        {'template_name': 'demo/components.html'},
        name='components',
    ),
    url(
        r'^buttons/$',
        views.BasePageView.as_view(),
        {'template_name': 'demo/buttons.html'},
        name='buttons',
    ),
    url(
        r'^full-width-banners/$',
        views.FullWidthBannersView.as_view(),
        {'template_name': 'demo/full-width-banners.html'},
        name='full-width-banners',
    ),
    url(
        r'^banners/$',
        views.BasePageView.as_view(),
        {'template_name': 'demo/banners.html'},
        name='banners',
    ),
    url(
        r'^message-boxes/$',
        views.BasePageView.as_view(),
        {'template_name': 'demo/message-boxes.html'},
        name='message-boxes',
    ),
    url(
        r'^cards/$',
        views.BasePageView.as_view(),
        {'template_name': 'demo/cards.html'},
        name='cards',
    ),
    url(
        r'^breadcrumbs/$',
        views.BreadcrumbsDemoPageView.as_view(),
        {'template_name': 'demo/breadcrumbs.html'},
        name='breadcrumbs',
    ),
    url(
        r'^search-page-components/$',
        views.SearchPageComponentsDemoPageView.as_view(),
        {'template_name': 'demo/search-page-components.html'},
        name='search-page-components',
    ),
    url(
        r'^fact-sheet/$',
        views.BasePageView.as_view(),
        {'template_name': 'demo/fact-sheet.html'},
        name='fact-sheet',
    ),
    url(
        r'^responsive/$',
        views.BasePageView.as_view(),
        {'template_name': 'demo/responsive.html'},
        name='responsive',
    ),
    url(
        r'^template-tags/$',
        views.BasePageView.as_view(),
        {'template_name': 'demo/cms.html'},
        name='cms-tags',
    ),
    url(
        r'^great-international-header-footer/$',
        views.InternationalHeaderView.as_view(),
        {'template_name': 'demo/great-international-header-footer.html'},
        name='great-international-header-footer',
    ),
    url(
        r'^invest-header/$',
        views.InvestHeaderView.as_view(),
        {'template_name': 'demo/invest-header.html'},
        name='invest-header',
    ),
    url(
        r'^google-tag-manager/$',
        views.BasePageView.as_view(),
        {'template_name': 'demo/google-tag-manager.html'},
        name='google-tag-manager',
    ),
    url(
        r'^pagination/$',
        views.DemoPaginationView.as_view(),
        name='pagination',
    ),
    url(
        r'^error-pages/$', views.BasePageView.as_view(), {'template_name': 'demo/error-pages.html'}, name='error-pages'
    ),
    url(
        r'^react-components/$',
        views.BasePageView.as_view(),
        {'template_name': 'demo/react-components.html'},
        name='react-components',
    ),
]

handler404 = 'directory_components.views.handler404'

handler500 = 'directory_components.views.handler500'
