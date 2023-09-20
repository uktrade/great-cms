from django.conf import settings
from django.utils.html import format_html
from django.utils.module_loading import import_string
from draftjs_exporter.dom import DOM
<<<<<<< HEAD
=======
from wagtail import VERSION as WAGTAIL_VERSION
>>>>>>> e80e8b749 (add tests)
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineEntityElementHandler,
)
from wagtail.rich_text import LinkHandler

# We can't use "anchor", as Wagtail uses this internally for links whose hrefs
# start with "#"
ANCHOR_TARGET_IDENTIFIER = 'anchor-target'


def render_a(attrs):
    return format_html('<a href="#{id}" id="{id}" data-id="{id}">', id=attrs['id'])


class AnchorIdentifierLinkHandler(LinkHandler):
    identifier = ANCHOR_TARGET_IDENTIFIER

    @classmethod
    def get_renderer(cls):
        renderer = getattr(cls, '_renderer', None)
        if renderer is None:
            renderer = getattr(settings, 'DRAFTAIL_ANCHORS_RENDERER', render_a)
            if isinstance(renderer, str):
                renderer = import_string(renderer)
            cls._renderer = renderer
        return renderer

    @classmethod
    def expand_db_attributes(cls, attrs):
        renderer = cls.get_renderer()
        return renderer(attrs)


def anchor_identifier_entity_decorator(props):
    """
    Draft.js ContentState to database HTML.
    Converts the ANCHOR entities into <a> tags.
    """
    return DOM.create_element(
        'a',
        {
            'data-id': props['anchor'].lstrip('#'),
            'id': props['anchor'].lstrip('#'),
            'href': f'#{props["anchor"].lstrip("#")}',
            # Add a custom linktype so we can handle the DB -> HTML transformation
            'linktype': ANCHOR_TARGET_IDENTIFIER,
        },
        props['children'],
    )


class AnchorIndentifierEntityElementHandler(InlineEntityElementHandler):
    """
    Database HTML to Draft.js ContentState.
    Converts the <a> tags into ANCHOR IDENTIFIER entities, with the right data.
    """

    # In Draft.js entity terms, anchors identifier are "mutable".
    mutability = 'MUTABLE'

    def get_attribute_data(self, attrs):
        """
        Take the ``anchor`` value from the ``href`` HTML attribute.
        """
        return {
            'anchor': attrs['href'].lstrip('#'),
            'data-id': attrs['id'],
        }
