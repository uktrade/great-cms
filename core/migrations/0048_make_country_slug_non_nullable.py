# Generated by Django 2.2.14 on 2021-01-11 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0047_backfill_country_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='slug',
            field=models.SlugField(max_length=100, unique=True),
        ),
    ]
