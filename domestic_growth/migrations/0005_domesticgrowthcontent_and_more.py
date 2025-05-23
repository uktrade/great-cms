# Generated by Django 4.2.19 on 2025-03-14 13:02

import wagtail.fields
import wagtail.search.index
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domestic_growth', '0004_domesticgrowthguidepage_domesticgrowthchildguidepage'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomesticGrowthContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_id', models.CharField()),
                ('title', models.CharField()),
                ('description', wagtail.fields.RichTextField(blank=True)),
                ('url', models.CharField(blank=True)),
            ],
            options={
                'ordering': ('title',),
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
        migrations.AlterField(
            model_name='domesticgrowthchildguidepage',
            name='body_sections',
            field=wagtail.fields.StreamField(
                [('section', 3)],
                blank=True,
                block_lookup={
                    0: ('wagtail.blocks.CharBlock', (), {}),
                    1: ('wagtail.snippets.blocks.SnippetChooserBlock', ('domestic_growth.DomesticGrowthContent',), {}),
                    2: ('wagtail.blocks.ListBlock', (1,), {'label': 'Choose snippet'}),
                    3: ('wagtail.blocks.StructBlock', [[('title', 0), ('intro', 0), ('content', 2)]], {}),
                },
                null=True,
            ),
        ),
    ]
