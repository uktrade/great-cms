from wagtail.admin.panels import FieldPanel, MultiFieldPanel


class DomesticGrowthHomePagePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Hero section',
            children=[
                FieldPanel('hero_image'),
                FieldPanel('hero_title'),
                FieldPanel('hero_intro'),
            ],
        ),
        MultiFieldPanel(
            heading='Explore section',
            children=[
                FieldPanel('explore_body'),
            ],
        ),
        MultiFieldPanel(
            heading='Guidance section',
            children=[
                FieldPanel('guidance_title'),
                FieldPanel('guidance_body'),
            ],
        ),
        MultiFieldPanel(
            heading='Case study section',
            children=[
                FieldPanel('case_study_title'),
                FieldPanel('case_study_intro'),
                FieldPanel('case_study_link_text'),
                FieldPanel('case_study_link_url'),
                FieldPanel('case_study_image'),
            ],
        ),
        MultiFieldPanel(
            heading='News section',
            children=[
                FieldPanel('news_title'),
                FieldPanel('news_link_text'),
                FieldPanel('news_link_url'),
                FieldPanel('news_link_text_extra'),
                FieldPanel('news_link_url_extra'),
            ],
        ),
        MultiFieldPanel(
            heading='Feedback section',
            children=[
                FieldPanel('feedback_title'),
                FieldPanel('feedback_description'),
                FieldPanel('feedback_link_text'),
                FieldPanel('feedback_link_url'),
            ],
        ),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]


class DomesticGrowthGuidePagePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Hero section',
            children=[
                FieldPanel('hero_title'),
                FieldPanel('hero_intro'),
            ],
        ),
        MultiFieldPanel(
            heading='Body section',
            children=[
                FieldPanel('body_title'),
                FieldPanel('body_intro'),
            ],
        ),
        MultiFieldPanel(
            heading='Primary regional support',
            children=[
                FieldPanel('primary_regional_support_title_england'),
                FieldPanel('primary_regional_support_intro_england'),
                FieldPanel('primary_regional_support_title_scotland'),
                FieldPanel('primary_regional_support_intro_scotland'),
                FieldPanel('primary_regional_support_title_ni'),
                FieldPanel('primary_regional_support_intro_ni'),
                FieldPanel('primary_regional_support_title_wales'),
                FieldPanel('primary_regional_support_intro_wales'),
            ],
        ),
        MultiFieldPanel(
            heading='Chambers of commerce',
            children=[
                FieldPanel('chamber_of_commerce_intro'),
            ],
        ),
        MultiFieldPanel(
            heading='Trade associations',
            children=[
                FieldPanel('trade_associations_title'),
                FieldPanel('trade_associations_intro'),
            ],
        ),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]


class DomesticGrowthChildGuidePagePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Body section',
            children=[
                FieldPanel('body_title'),
                FieldPanel('body_intro'),
                FieldPanel('body_sections'),
            ],
        ),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]


class DomesticGrowthAboutPagePanels:
    content_panels = [
        MultiFieldPanel(
            heading='Heading',
            children=[
                FieldPanel('heading'),
            ],
        ),
        MultiFieldPanel(
            heading='Body section',
            children=[
                FieldPanel('body'),
            ],
        ),
    ]

    settings_panels = [FieldPanel('title'), FieldPanel('slug')]
