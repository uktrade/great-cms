# Generated by Django 4.1.13 on 2024-01-11 11:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0128_alter_sharesettings_hashtags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='greatmedia',
            name='subtitles_en',
            field=models.TextField(
                help_text='English-language subtitles for this video, in VTT format, Required for Level A WCAG compliance.',
                null=True,
                verbose_name='English subtitles',
            ),
        ),
        migrations.AlterField(
            model_name='greatmedia',
            name='transcript',
            field=models.TextField(blank=True, null=True, verbose_name='Transcript'),
        ),
    ]
