# Generated by Django 4.1.10 on 2023-09-07 12:33

import django.db.models.deletion
import modelcluster.fields
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('export_academy', '0024_event_description_long_event_outcomes'),
        ('core', '0107_alter_getintouchpage_page_body_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('role', models.CharField(max_length=255)),
                ('organisation', models.CharField(max_length=255)),
                ('description', wagtail.fields.RichTextField()),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='SpeakerOrderable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                (
                    'page',
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='event_speakers',
                        to='export_academy.event',
                    ),
                ),
                ('speaker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.speaker')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
