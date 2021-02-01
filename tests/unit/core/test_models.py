import time
from unittest import mock

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import RequestFactory, TestCase
from wagtail.admin.edit_handlers import ObjectList
from wagtail.core.blocks.stream_block import StreamBlockValidationError
from wagtail.core.models import Collection
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.tests.utils import WagtailPageTests, WagtailTestUtils
from wagtail_factories import ImageFactory

from core.mixins import AuthenticatedUserRequired
from core.models import (
    AbstractObjectHash,
    CaseStudyRelatedPages,
    Country,
    CuratedListPage,
    DetailPage,
    IndustryTag,
    InterstitialPage,
    LandingPage,
    LessonPlaceholderPage,
    ListPage,
    MagnaPageChooserPanel,
    Product,
    Region,
    Tag,
    TopicPage,
    case_study_body_validation,
)
from domestic.models import DomesticDashboard, DomesticHomePage
from exportplan.models import ExportPlanDashboardPage
from tests.helpers import make_test_video
from tests.unit.core import factories
from .factories import (
    CaseStudyFactory,
    DetailPageFactory,
    LessonPlaceholderPageFactory,
    TopicPageFactory,
)


def test_object_hash():
    mocked_file = mock.Mock()
    mocked_file.read.return_value = b'foo'
    hash = AbstractObjectHash.generate_content_hash(mocked_file)
    assert hash == 'acbd18db4cc2f85cedef654fccc4a4d8'


@pytest.mark.django_db
def test_detail_page_can_mark_as_read(client, domestic_homepage, user, domestic_site):
    # given the user has not read a lesson
    client.force_login(user)

    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    curated_list_page = factories.CuratedListPageFactory(parent=list_page)
    topic_page = factories.TopicPageFactory(parent=curated_list_page)
    detail_page = factories.DetailPageFactory(parent=topic_page)

    client.get(detail_page.url)

    # then the progress is saved
    read_hit = detail_page.page_views.get()
    assert read_hit.sso_id == str(user.pk)
    assert read_hit.list_page == list_page


@pytest.mark.django_db
def test_detail_page_cannot_mark_as_read(client, domestic_homepage, user, domestic_site):
    # given the user has not read a lesson
    client.force_login(user)
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=False)
    curated_list_page = factories.CuratedListPageFactory(parent=list_page)
    topic_page = factories.TopicPageFactory(parent=curated_list_page)
    detail_page = factories.DetailPageFactory(parent=topic_page)

    client.get(detail_page.url)

    # then the progress is saved
    assert detail_page.page_views.count() == 0


@pytest.mark.django_db
def test_detail_page_anon_user_not_marked_as_read(client, domestic_homepage, domestic_site):
    # given the user has not read a lesson
    clp = factories.CuratedListPageFactory(parent=domestic_homepage)
    topic_page = factories.TopicPageFactory(parent=clp)
    detail_page = factories.DetailPageFactory(parent=topic_page)

    client.get(detail_page.url)

    # then the progress is unaffected
    assert detail_page.page_views.count() == 0


@pytest.mark.django_db
def test_curated_list_page_has_link_in_context_back_to_parent(
    client,
    domestic_homepage,
    domestic_site,
    patch_export_plan,
    patch_get_user_lesson_completed,
    user,
):

    list_page = factories.ListPageFactory(
        parent=domestic_homepage, record_read_progress=False, slug='example-learning-homepage'
    )
    curated_list_page = factories.CuratedListPageFactory(parent=list_page, slug='example-module')

    expected_url = list_page.url
    assert expected_url == '/example-learning-homepage/'

    client.force_login(user)  # because unauthed users get redirected

    resp = client.get(curated_list_page.url)

    # Make a more precise string to search for: one that's marked up as a
    # hyperlink target, at least
    expected_link_string = f'href="{expected_url}"'
    assert expected_link_string.encode('utf-8') in resp.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    'querystring_to_add,expected_backlink_value',
    (
        ('', None),
        ('?return-link=%2Fexport-plan%2Fsection%2Fabout-your-business%2F', '/export-plan/section/about-your-business/'),
        (
            '?return-link=%2Fexport-plan%2Fsection%2Fabout-your-business%2F%3Ffoo%3Dbar',
            '/export-plan/section/about-your-business/?foo=bar',
        ),
        (
            '?bam=baz&return-link=%2Fexport-plan%2Fsection%2Fabout-your-business%2F%3Ffoo%3Dbar',
            '/export-plan/section/about-your-business/?foo=bar',  # NB: bam=baz should not be here
        ),
        ('?bam=baz&return-link=example%2Fexport-plan%2Fpath%2F%3Ffoo%3Dbar', None),
        (
            (
                '?bam=baz&return-link=https%3A%2F%2Fphishing.example.com'
                '%2Fexport-plan%2Fsection%2Fabout-your-business%2F%3Ffoo%3Dbar'
            ),
            None,
        ),
        (
            (
                '?bam=baz&return-link=%3A%2F%2Fphishing.example.com'
                '%2Fexport-plan%2Fsection%2Fabout-your-business%2F%3Ffoo%3Dbar'
            ),
            None,
        ),
        ('?bam=baz', None),
        (
            '?bam=baz&return-link=%2Fexport-plan%2Fsection%2Fabout-your-business%2F%3Ffoo%3Dbar',
            '/export-plan/section/about-your-business/?foo=bar',
        ),
    ),
    ids=(
        'no backlink querystring present',
        'backlink querystring present without encoded querystring of its own',
        'backlink querystring present WITH encoded querystring of its own',
        'backlink querystring present WITH encoded querystring and other args',
        'backlink querystring present WITH bad payload - path does not start with / ',
        'backlink querystring present WITH bad payload - path is a full URL',
        'backlink querystring present WITH bad payload - path is a URL with flexible proto',
        'backlink querystring NOT present BUT another querystring is',
        'backlink querystring present WITH OTHER QUERYSTRING TOO',
    ),
)
def test_detail_page_get_context_handles_backlink_querystring_appropriately(
    rf, domestic_homepage, domestic_site, user, querystring_to_add, expected_backlink_value
):

    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=False)
    curated_list_page = factories.CuratedListPageFactory(parent=list_page)
    topic_page = factories.TopicPageFactory(parent=curated_list_page)
    detail_page = factories.DetailPageFactory(parent=topic_page, template='learn/detail_page.html')

    lesson_page_url = detail_page.url
    if querystring_to_add:
        lesson_page_url += querystring_to_add

    request = rf.get(lesson_page_url)
    request.user = user
    request.user.export_plan.data = mock.Mock('mocked-export-plan')

    context = detail_page.get_context(request)

    if expected_backlink_value is None:
        assert 'backlink' not in context
    else:
        assert context.get('backlink') == expected_backlink_value


@pytest.mark.django_db
@pytest.mark.parametrize(
    'backlink_path,expected',
    (
        (None, None),
        ('', None),
        ('/export-plan/section/about-your-business/', 'About your business'),
        ('/export-plan/section/business-objectives/', 'Business objectives'),
        ('/export-plan/section/target-markets-research/', 'Target markets research'),
        ('/export-plan/section/adaptation-for-your-target-market/', 'Adaptation for your target market'),
        ('/export-plan/section/marketing-approach/', 'Marketing approach'),
        ('/export-plan/section/costs-and-pricing/', 'Costs and pricing'),
        ('/export-plan/section/funding-and-credit/', 'Funding and Credit'),
        ('/export-plan/section/payment-methods/', 'Payment methods'),
        ('/export-plan/section/travel-and-business-policies/', 'Travel and business policies'),
        ('/export-plan/section/business-risk/', 'Business risk'),
        ('/export-plan/section/adaptation-for-your-target-market/?foo=bar', 'Adaptation for your target market'),
        ('/export-plan/', None),
        ('/path/that/will/not/match/anything/', None),
    ),
    ids=(
        'no backlink',
        'empty string backlink',
        'Seeking: About your business',
        'Seeking: Business objectives',
        'Seeking: Target markets research',
        'Seeking: Adaptation for your target market',
        'Seeking: Marketing approach',
        'Seeking: Costs and pricing',
        'Seeking: Payment methods',
        'Seeking: Funding and Credit',
        'Seeking: Travel and business policies',
        'Seeking: Business risk',
        'Valid backlink with querystring does not break name lookup',
        'backlink for real page that is not an export plan step',
        'backlink for a non-existent page',
    ),
)
def test_detail_page_get_context_gets_backlink_title_based_on_backlink(backlink_path, expected):
    detail_page = factories.DetailPageFactory(template='learn/detail_page.html')
    assert detail_page._get_backlink_title(backlink_path) == expected


@pytest.mark.django_db
def test_case_study__str_method():
    case_study = CaseStudyFactory(title='', company_name='Test Co')
    assert f'{case_study}' == 'Test Co'

    case_study = CaseStudyFactory(title='Alice and Bob export to every continent', company_name='Test Co')
    assert f'{case_study}' == 'Alice and Bob export to every continent'


@pytest.mark.django_db
def test_case_study__timestamps():
    case_study = CaseStudyFactory(company_name='Test Co')
    created = case_study.created
    modified = case_study.created
    assert created == modified

    time.sleep(1)  # Forgive this - we need to have a real, later save
    case_study.save()
    case_study.refresh_from_db()

    assert case_study.created == created
    assert case_study.modified > modified


_case_study_top_level_error_message = (
    'This block must contain one Media section (with one or two items in it) and one Text section.'
)

_case_study_one_video_only_error_message = 'Only one video may be used in a case study.'
_case_study_video_order_error_message = 'The video must come before a still image.'


@pytest.mark.django_db
@pytest.mark.parametrize(
    'block_type_values,exception_message',
    (
        (['text'], _case_study_top_level_error_message),
        ([('media', ('video',))], _case_study_top_level_error_message),
        ([], None),
        (['text', 'text'], _case_study_top_level_error_message),
        (['text', ('media', ('video', 'image'))], _case_study_top_level_error_message),
        ([('media', ('video',)), ('media', ('video',))], _case_study_top_level_error_message),
        (['text', ('media', ('video', 'image')), 'text'], _case_study_top_level_error_message),
        ([('media', ('video', 'image')), 'text', ('media', ('video', 'image'))], _case_study_top_level_error_message),
        ([('media', ('video', 'image')), 'text'], None),
        ([('media', ('video',)), 'text'], None),
        ([('media', ('image',)), 'text'], None),
        ([('media', ('image', 'image')), 'text'], None),
        ([('media', ('image', 'video')), 'text'], _case_study_video_order_error_message),
        ([('media', ('video', 'video')), 'text'], _case_study_one_video_only_error_message),
    ),
    ids=(
        '1. Top-level check: text node only: not fine',
        '2. Top-level check: media node only: not fine',
        '3. Top-level check: no nodes: fine - requirement is done at a higher level',
        '4. Top-level check: two text nodes: not fine',
        '5. Top-level check: text before media: not fine',
        '6. Top-level check: two media nodes: not fine',
        '7. Top-level check: text, media, text: not fine',
        '8. Top-level check: media, text, media: not fine',
        '9. media node (video and image) and text node: fine',
        '10. media node (video only) and text node: fine',
        '11. media node (image only) and text node: fine',
        '12. media node (two images) and text node: fine',
        '13. media node (image before video) and text node: not fine',
        '14. media node (two videos) and text node: not fine',
    ),
)
def test_case_study_body_validation(block_type_values, exception_message):
    def _create_block(block_type):
        mock_block = mock.Mock()
        mock_block.block_type = block_type
        return mock_block

    value = []
    for block_spec in block_type_values:
        if type(block_spec) == tuple:
            parent_block = _create_block(block_spec[0])
            children = []
            for subblock_spec in block_spec[1]:
                children.append(_create_block(subblock_spec))
            parent_block.value = children
            value.append(parent_block)
        else:
            value.append(_create_block(block_spec))

    if exception_message:
        with pytest.raises(StreamBlockValidationError) as ctx:
            case_study_body_validation(value)
            assert ctx.message == exception_message
    else:
        # should not blow up
        case_study_body_validation(value)


class LandingPageTests(WagtailPageTests):
    def test_can_be_created_under_homepage(self):
        self.assertAllowedParentPageTypes(LandingPage, {DomesticHomePage})

    def test_can_be_created_under_landing_page(self):
        self.assertAllowedSubpageTypes(
            LandingPage, {ListPage, InterstitialPage, ExportPlanDashboardPage, DomesticDashboard}
        )


class ListPageTests(WagtailPageTests):
    def test_can_be_created_under_landing_page(self):
        self.assertAllowedParentPageTypes(ListPage, {LandingPage})

    def test_allowed_subtypes(self):
        self.assertAllowedSubpageTypes(ListPage, {CuratedListPage})


class CuratedListPageTests(WagtailPageTests):
    def test_can_be_created_under_list_page(self):
        self.assertAllowedParentPageTypes(CuratedListPage, {ListPage})

    def test_allowed_subtypes(self):
        self.assertAllowedSubpageTypes(CuratedListPage, {TopicPage})


@pytest.mark.django_db
def test_curatedlistpage_count_detail_pages(curated_list_pages_with_lessons):
    data = curated_list_pages_with_lessons
    clp_1 = data[0][0]
    clp_2 = data[1][0]

    assert clp_1.count_detail_pages == 2  # 2 pages, placeholder ignored
    assert clp_2.count_detail_pages == 1  # 1 page only, no placeholders at all


class TopicPageTests(WagtailPageTests):
    def test_parent_page_types(self):
        self.assertAllowedParentPageTypes(TopicPage, {CuratedListPage})

    def test_allowed_subtypes(self):
        self.assertAllowedSubpageTypes(
            TopicPage,
            {
                DetailPage,
                LessonPlaceholderPage,
            },
        )


@pytest.mark.django_db
def test_topic_page_redirects_to_module(
    rf,
    domestic_homepage,
    domestic_site,
):
    # The topic pages should never render their own content - they are basically
    # scaffolding to give us a sensible page tree. As such they shouldn't be
    # rendered
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=False)
    curated_list_page = factories.CuratedListPageFactory(parent=list_page)
    topic_page = TopicPageFactory(
        parent=curated_list_page,
    )

    # Check that we have the page tree set up correctly, else this is None
    assert curated_list_page.url is not None

    for page_method in ('serve', 'serve_preview'):

        request = rf.get(topic_page.url)

        resp = getattr(topic_page, page_method)(request)

        assert resp._headers['location'] == ('Location', curated_list_page.url)


class LessonPlaceholderPageTests(WagtailPageTests):
    def test_parent_page_types(self):
        self.assertAllowedParentPageTypes(LessonPlaceholderPage, {TopicPage})

    def test_allowed_subtypes(self):
        self.assertAllowedSubpageTypes(LessonPlaceholderPage, {})


@pytest.mark.django_db
def test_context_cms_generic_page(rf, domestic_homepage):
    assert 'page' in domestic_homepage.get_context(rf)


@pytest.mark.django_db
def test_placeholder_page_redirects_to_module(
    rf,
    domestic_homepage,
    domestic_site,
):
    # The topic pages should never render their own content and instead redirect
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=False)
    curated_list_page = factories.CuratedListPageFactory(parent=list_page)
    topic_page = TopicPageFactory(
        parent=curated_list_page,
    )
    placeholder_page = LessonPlaceholderPageFactory(parent=topic_page)

    # Check that we have the page tree set up correctly, else this is None
    assert curated_list_page.url is not None

    for page_method in ('serve', 'serve_preview'):

        request = rf.get(placeholder_page.url)

        resp = getattr(placeholder_page, page_method)(request)

        assert resp._headers['location'] == ('Location', curated_list_page.url)


class DetailPageTests(WagtailPageTests):
    def test_parent_page_types(self):
        self.assertAllowedParentPageTypes(DetailPage, {TopicPage})

    def test_detail_page_creation_for_single_hero_image(self):
        detail_page = DetailPageFactory(hero=[('Image', ImageFactory())])
        self.assert_(detail_page, True)

    def test_validation_kick_for_multiple_hero_image(self):
        with pytest.raises(ValidationError):
            detail_page = DetailPageFactory(hero=[('Image', ImageFactory()), ('Image', ImageFactory())])
            self.assert_(detail_page, None)


@pytest.mark.django_db
def test_redirection_for_unauthenticated_user(
    client,
    domestic_homepage,
    domestic_site,
    patch_export_plan,
    patch_get_user_lesson_completed,
    user,
):

    landing_page = factories.LandingPageFactory(parent=domestic_homepage)
    interstitial_page = factories.InterstitialPageFactory(parent=landing_page)
    list_page = factories.ListPageFactory(parent=domestic_homepage)
    curated_list_page = factories.CuratedListPageFactory(parent=list_page)
    topic_page = factories.TopicPageFactory(parent=curated_list_page)
    detail_page = factories.DetailPageFactory(parent=topic_page)

    pages = [
        landing_page,
        interstitial_page,
        list_page,
        curated_list_page,
        detail_page,
    ]

    for page in pages:
        assert isinstance(page, AuthenticatedUserRequired)

    for page in pages:
        response = client.get(page.url, follow=False)
        assert response.status_code == 302
        assert response._headers['location'] == ('Location', '/login/')

    # Show an authenticated user can still get in there
    client.force_login(user)
    for page in pages:
        response = client.get(page.url, follow=False)
        assert response.status_code == 200


class TestImageAltRendition(TestCase, WagtailTestUtils):
    def setUp(self):
        self.login()
        root_collection = Collection.objects.create(name='Root', depth=0)
        great_image_collection = root_collection.add_child(name='Great Images')

        # Create an image with alt text
        AltTextImage = get_image_model()  # Noqa
        self.image = AltTextImage.objects.create(
            title='Test image', file=get_test_image_file(), alt_text='smart alt text', collection=great_image_collection
        )

    def test_image_alt_rendition(self):
        rendition = self.image.get_rendition('width-100')
        assert rendition.alt == 'smart alt text'
        assert self.image.title != rendition.alt


class TestGreatMedia(TestCase):
    def test_sources_mp4_with_no_transcript(self):
        media = make_test_video()
        self.assertEqual(
            media.sources,
            [
                {
                    'src': '/media/movie.mp4',
                    'type': 'video/mp4',
                    'transcript': None,
                }
            ],
        )

    def test_sources_mp4_with_transcript(self):
        media = make_test_video(transcript='A test transcript text')

        self.assertEqual(
            media.sources,
            [
                {
                    'src': '/media/movie.mp4',
                    'type': 'video/mp4',
                    'transcript': 'A test transcript text',
                }
            ],
        )


class TestSmallSnippets(TestCase):
    # Most snippets are generally small models. Move them out of this test case
    # into their own if/when they gain any custom methods beyond __str__

    def test_region(self):
        region = Region.objects.create(name='Test Region')
        self.assertEqual(region.name, 'Test Region')
        self.assertEqual(f'{region}', 'Test Region')  #  tests __str__

    def test_country(self):
        region = Region.objects.create(name='Test Region')

        # NB: slugs are not automatically set.
        # The SlugField is about valiation, not auto-population by default
        country1 = Country.objects.create(
            name='Test Country',
            slug='test-country',
        )
        country2 = Country.objects.create(
            name='Other Country',
            slug='other-country',
            region=region,
        )
        country_unicode = Country.objects.create(
            name='Téßt Country',
            slug='tt-country',
        )

        self.assertEqual(country1.name, 'Test Country')
        self.assertEqual(country1.slug, 'test-country')
        self.assertEqual(country1.region, None)
        self.assertEqual(f'{country1}', 'Test Country')  #  tests __str__

        self.assertEqual(country2.name, 'Other Country')
        self.assertEqual(country2.slug, 'other-country')
        self.assertEqual(country2.region, region)

        self.assertEqual(country_unicode.name, 'Téßt Country')
        # by default, ASCII only - https://docs.djangoproject.com/en/2.2/ref/utils/#django.utils.text.slugify
        self.assertEqual(country_unicode.slug, 'tt-country')
        self.assertEqual(country_unicode.region, None)
        self.assertEqual(f'{country_unicode}', 'Téßt Country')  #  tests __str__

    def test_country_sets_slug_on_save(self):
        country = Country.objects.create(name='Test Country')
        country.refresh_from_db()
        self.assertEqual(country.slug, 'test-country')

        # Slug is set only on first save, if not already set
        country_2 = Country.objects.create(name='Another Country')
        self.assertEqual(country_2.slug, 'another-country')
        country_2.name = 'Changed country name'
        country_2.save()
        country_2.refresh_from_db()
        self.assertEqual(
            country_2.slug,
            'another-country',
            'Slug should not have changed',
        )

        # Can specify slug up-front
        country_3 = Country.objects.create(
            name='Country Three',
            slug='somewhere',
        )
        country_3.refresh_from_db()
        self.assertEqual(country_3.slug, 'somewhere')

        # Can't reuse slug
        with self.assertRaises(IntegrityError):
            Country.objects.create(name='Test Country')

    def test_product(self):
        product = Product.objects.create(name='Test Product')
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(f'{product}', 'Test Product')  #  tests __str__

    def test_tag(self):
        tag = Tag.objects.create(name='Test Tag')
        self.assertEqual(tag.name, 'Test Tag')
        self.assertEqual(f'{tag}', 'Test Tag')  #  tests __str__

    def test_industry_tag(self):
        tag = IndustryTag.objects.create(name='Test IndustryTag')
        self.assertEqual(tag.name, 'Test IndustryTag')
        self.assertEqual(f'{tag}', 'Test IndustryTag')  #  tests __str__


class TestMagnaPageChooserPanel(TestCase):
    def setUp(self):
        self.request = RequestFactory().get('/')
        user = AnonymousUser()  # technically, Anonymous users cannot access the admin
        self.request.user = user

        model = CaseStudyRelatedPages  # a model with a foreign key to Page which we want to render as a page chooser

        # a MagnaPageChooserPanel class that works on CaseStudyRelatedPages's 'page' field
        self.edit_handler = ObjectList(
            [MagnaPageChooserPanel('page', [DetailPage, CuratedListPage, TopicPage])]
        ).bind_to(model=model, request=self.request)
        self.my_page_chooser_panel = self.edit_handler.children[0]

        # build a form class containing the fields that MyPageChooserPanel wants
        self.PageChooserForm = self.edit_handler.get_form_class()

        # a test instance of PageChooserModel, pointing to the 'christmas' page
        self.detail_page = DetailPageFactory(slug='detail-page')
        self.test_instance = model.objects.create(page=self.detail_page)

        self.form = self.PageChooserForm(instance=self.test_instance)
        self.page_chooser_panel = self.my_page_chooser_panel.bind_to(instance=self.test_instance, form=self.form)

    def test_magna_page_chooser_panel_target_models(self):
        result = (
            MagnaPageChooserPanel('page', [DetailPage, CuratedListPage, TopicPage])
            .bind_to(model=MagnaPageChooserPanel)
            .target_models()
        )
        self.assertEqual(result, [DetailPage, CuratedListPage, TopicPage])

    def test_magna_page_chooser_panel_render_as_empty_field(self):
        test_instance = CaseStudyRelatedPages()
        form = self.PageChooserForm(instance=test_instance)
        page_chooser_panel = self.my_page_chooser_panel.bind_to(instance=test_instance, form=form, request=self.request)
        result = page_chooser_panel.render_as_field()

        self.assertIn('<span class="title"></span>', result)
        self.assertIn('Choose a page', result)
