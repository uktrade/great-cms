from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from django import forms
from core import models


class MetaDataBlock(blocks.StructBlock):
    label = blocks.CharBlock(required=True)
    value = blocks.CharBlock(required=True)


class ReviewBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    quote = blocks.TextBlock(required=True, help_text='Enter a quote (*required)')
    name = blocks.TextBlock(required=False)
    role = blocks.TextBlock(required=False)
    company_name = blocks.TextBlock(required=False)

class SeriesBlock(blocks.StructBlock):
    course_name = blocks.CharBlock(max_length=255,required=False)
    course_description= blocks.CharBlock(max_length=255,required=False)
    course_image=ImageChooserBlock(required=False) 
    course_feature_one=blocks.CharBlock(max_length=255,required=False)
    course_feature_two=blocks.CharBlock(max_length=255,required=False)
    course_feature_three=blocks.CharBlock(max_length=255,required=False)
    course_cta_text=blocks.CharBlock(max_length=255,required=False)
    course_cta_url=blocks.CharBlock(max_length=255,required=False)

