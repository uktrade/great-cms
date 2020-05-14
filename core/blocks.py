from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock


class LinkBlock(blocks.StructBlock):
    text = blocks.CharBlock(max_length=255, required=False)
    url = blocks.CharBlock(max_length=255, required=False)  # not a URL block to allow relative links


class HeroBlock(LinkBlock):
    text = blocks.RichTextBlock()
    image = ImageChooserBlock()


class LinkWithSourceBlock(LinkBlock):
    source = blocks.CharBlock(help_text='The source or the type of the link, e.g. GOV.UK/Advice')


class LinkWithImageAndContentBlock(LinkWithSourceBlock):
    content = blocks.RichTextBlock()
    image = ImageChooserBlock()


class MediaChooserBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        """Render implemented in the VideoBlock, this block shouldn't be used in its own."""
        pass


class VideoBlock(blocks.StructBlock):
    width = blocks.IntegerBlock()
    height = blocks.IntegerBlock()
    video = MediaChooserBlock()


class CuratedTopicBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=255)
    pages = blocks.ListBlock(blocks.PageChooserBlock(label='Detail page'))

    class Meta:
        template = 'core/curated_topic.html'


class LinkStructValue(blocks.StructValue):
    """
    Generates a URL for blocks with multiple link choices.
    """
    @property
    def url(self):
        page = self.get('internal_link')
        ext = self.get('external_link')
        if page:
            return page.url
        else:
            return ext


class LinkBlock(blocks.StructBlock):
    internal_link = blocks.PageChooserBlock(
        required=False,
        label='Internal link',
    )
    external_link = blocks.CharBlock(
        required=False,
        max_length=255,
        label='External link',
    )

    class Meta:
        value_class = LinkStructValue


class ButtonBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=255)
    link = LinkBlock(required=False)

    class Meta:
        template = 'core/button.html'
