# Generated by Django 4.1.10 on 2023-09-08 13:48

from django.db import migrations, models

from export_academy.models import Event


def migrate_data_forward(apps, schema_editor):
    for instance in Event.objects.all():
        instance.save()  # Will trigger slug update


class Migration(migrations.Migration):
    dependencies = [
        ('export_academy', '0024_event_description_long_event_outcomes'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='slug',
            field=models.SlugField(unique=True, null=True, max_length=255),
            preserve_default=False,
        )
    ]
