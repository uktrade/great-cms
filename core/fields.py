from django.db.models import TextField
from wagtail import blocks
from wagtail.fields import StreamField


def single_struct_block_stream_field_factory(
    field_name,
    block_class_instance,
    max_num=None,
    min_num=None,
    required=False,
    **kwargs,
):
    field = StreamField(
        blocks.StreamBlock(
            [(field_name, block_class_instance)],
            max_num=max_num,
            min_num=min_num,
            required=required,
        ),
        use_json_field=True,
        **kwargs,
    )
    return field


# Do not delete - needed for a temporary legacy migration dependency
class MarkdownField(TextField):
    pass
