from django.db.models import TextField

from wagtail.core import blocks
from wagtail.core.fields import StreamField

from core.widgets import MarkdownTextarea


def single_struct_block_stream_field_factory(
    field_name, block_class_instance, max_num=None, min_num=None, required=False, **kwargs
):
    field = StreamField(
        blocks.StreamBlock([(field_name, block_class_instance)], max_num=max_num, min_num=min_num, required=required),
        **kwargs,
    )
    return field


class MarkdownField(TextField):
    def formfield(self, **kwargs):
        defaults = {'widget': MarkdownTextarea}
        defaults.update(kwargs)
        return super(MarkdownField, self).formfield(**defaults)
