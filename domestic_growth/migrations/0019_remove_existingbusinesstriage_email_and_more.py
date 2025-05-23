# Generated by Django 4.2.19 on 2025-04-14 09:56

import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domestic_growth', '0018_alter_existingbusinesstriage_currently_export'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='existingbusinesstriage',
            name='email',
        ),
        migrations.RemoveField(
            model_name='startingabusinesstriage',
            name='email',
        ),
        migrations.CreateModel(
            name='StartingABusinessGuideEmailRecipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, null=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, null=True, verbose_name='modified'
                    ),
                ),
                ('email', models.EmailField(max_length=255)),
                (
                    'triage',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING, to='domestic_growth.startingabusinesstriage'
                    ),
                ),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExistingBusinessGuideEmailRecipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'created',
                    django_extensions.db.fields.CreationDateTimeField(
                        auto_now_add=True, null=True, verbose_name='created'
                    ),
                ),
                (
                    'modified',
                    django_extensions.db.fields.ModificationDateTimeField(
                        auto_now=True, null=True, verbose_name='modified'
                    ),
                ),
                ('email', models.EmailField(max_length=255)),
                (
                    'triage',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING, to='domestic_growth.existingbusinesstriage'
                    ),
                ),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
    ]
