# Generated by Django 4.2.19 on 2025-03-25 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domestic_growth', '0011_alter_existingbusinesstriage_turnover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='existingbusinesstriage',
            name='currently_export',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
