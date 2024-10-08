# Generated by Django 4.2.15 on 2024-09-25 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('international_online_offer', '0054_triagedata_sector_id_triagedata_sector_sub_sub_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='address_line_1',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='userdata',
            name='address_line_2',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='userdata',
            name='duns_number',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='userdata',
            name='postcode',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='userdata',
            name='town',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
