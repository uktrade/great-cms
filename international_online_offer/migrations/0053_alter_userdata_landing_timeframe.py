# Generated by Django 4.2.11 on 2024-07-19 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('international_online_offer', '0052_alter_triagedata_location_none'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='landing_timeframe',
            field=models.CharField(
                choices=[
                    ('UNDER_SIX_MONTHS', 'In the next 6 months'),
                    ('SIX_TO_TWELVE_MONTHS', '6 to 12 months'),
                    ('ONE_TO_TWO_YEARS', '1 to 2 years'),
                    ('OVER_TWO_YEARS', "In more than 2 years' time"),
                ],
                default=None,
                max_length=255,
                null=True,
            ),
        ),
    ]
