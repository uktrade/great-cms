# Generated by Django 2.2.14 on 2021-01-11 12:16

from django.db import migrations
from django.utils.text import slugify


def forwards(apps, schema_editor):
    Country = apps.get_model('core', 'Country')
    for country in Country.objects.all():
        country.slug = slugify(country.name)
        country.save()


def backwards(apps, schema_editor):
    Country = apps.get_model('core', 'Country')
    for country in Country.objects.all():
        country.slug = None
        country.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0046_add_v1_snippet_models'),
    ]

    operations = [migrations.RunPython(forwards, backwards)]
