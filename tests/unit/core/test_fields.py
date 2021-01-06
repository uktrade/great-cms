import pytest
from wagtail.core import blocks
from wagtail.core.fields import StreamField

from core import fields


@pytest.mark.django_db
def test_single_struct_block_stream_field_factory():
    field = fields.single_struct_block_stream_field_factory(
        'test', block_class_instance=blocks.TextBlock(), max_num=6, min_num=1, null=True, blank=True
    )
    assert isinstance(field, StreamField)
    assert field.null is True
    assert field.blank is True
    assert field.stream_block._constructor_kwargs == {'max_num': 6, 'min_num': 1, 'required': False}
    assert isinstance(field.stream_block.child_blocks['test'], blocks.TextBlock)
