# Generated by Django 4.1.9 on 2023-05-24 15:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('core', '0085_auto_20230509_0933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentmoduletag',
            name='tag',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='%(app_label)s_%(class)s_items',
                to='taggit.tag',
            ),
        ),
    ]
