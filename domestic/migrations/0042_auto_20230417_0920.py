# Generated by Django 3.2.18 on 2023-04-17 09:20

import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('domestic', '0041_alter_articlepage_article_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='greatdomestichomepage',
            name='slice_columns',
            field=wagtail.fields.StreamField(
                [
                    (
                        'columns',
                        wagtail.blocks.StructBlock(
                            [
                                ('title', wagtail.blocks.CharBlock()),
                                ('url', wagtail.blocks.CharBlock()),
                                (
                                    'source',
                                    wagtail.blocks.CharBlock(
                                        help_text='The source or the type of the link, e.g. GOV.UK/Advice',
                                        required=False,
                                    ),
                                ),
                                ('image', wagtail.images.blocks.ImageChooserBlock()),
                                (
                                    'summary',
                                    wagtail.blocks.RichTextBlock(
                                        features=[
                                            'h2',
                                            'h3',
                                            'h4',
                                            'bold',
                                            'italic',
                                            'ol',
                                            'ul',
                                            'hr',
                                            'link',
                                            'document-link',
                                        ],
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                use_json_field=True,
                blank=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='greatdomestichomepage',
            name='slice_title',
            field=models.TextField(blank=True, null=True),
        ),
    ]
