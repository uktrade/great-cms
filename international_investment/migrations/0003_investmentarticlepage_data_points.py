# Generated by Django 4.2.14 on 2024-09-10 13:33

import wagtail.blocks
import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('international_investment', '0002_investmentsectorspage_investmentregionspage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='investmentarticlepage',
            name='data_points',
            field=wagtail.fields.StreamField(
                [
                    (
                        'points',
                        wagtail.blocks.StreamBlock(
                            [
                                (
                                    'data_point',
                                    wagtail.blocks.StructBlock(
                                        [
                                            ('title', wagtail.blocks.CharBlock(label='Title', max_length=255)),
                                            (
                                                'description',
                                                wagtail.blocks.CharBlock(
                                                    label='Description', max_length=255, required=False
                                                ),
                                            ),
                                        ]
                                    ),
                                )
                            ],
                            block_counts={'data_point': {'min_num': 1}},
                        ),
                    )
                ],
                blank=True,
                null=True,
                use_json_field=True,
            ),
        ),
    ]
