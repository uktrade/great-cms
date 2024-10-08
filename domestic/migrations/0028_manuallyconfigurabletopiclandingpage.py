# Generated by Django 2.2.20 on 2021-04-22 08:58

import django.db.models.deletion
import great_components.mixins
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models

import core.mixins
import domestic.cms_panels


class Migration(migrations.Migration):
    dependencies = [
        ('wagtailcore', '0059_apply_collection_ordering'),
        ('core', '0065_delete_wagtail_personalisation_migration_references'),
        ('domestic', '0027_flip_trade_finance_snippet_to_page'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManuallyConfigurableTopicLandingPage',
            fields=[
                (
                    'page_ptr',
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to='wagtailcore.Page',
                    ),
                ),
                ('hero_teaser', models.CharField(blank=True, max_length=255, null=True)),
                ('banner_text', wagtail.fields.RichTextField(blank=True)),
                ('teaser', models.TextField(blank=True)),
                (
                    'panels',
                    wagtail.fields.StreamField(
                        [
                            (
                                'panel',
                                wagtail.blocks.StructBlock(
                                    [
                                        ('link_text', wagtail.blocks.CharBlock()),
                                        ('link_url', wagtail.blocks.CharBlock()),
                                        ('image', wagtail.images.blocks.ImageChooserBlock(required=False)),
                                        ('description', wagtail.blocks.TextBlock()),
                                    ]
                                ),
                            )
                        ],
                        use_json_field=True,
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    'hero_image',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='+',
                        to='core.AltTextImage',
                    ),
                ),
            ],
            options={
                'abstract': False,
            },
            bases=(
                domestic.cms_panels.ManuallyConfigurableTopicLandingPagePanels,
                'wagtailcore.page',
                core.mixins.WagtailGA360Mixin,
                great_components.mixins.GA360Mixin,
            ),
        ),
    ]
