# Generated by Django 4.2.15 on 2024-09-26 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('international_online_offer', '0055_userdata_address_line_1_userdata_address_line_2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='county',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
