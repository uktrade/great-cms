# Generated by Django 4.1.10 on 2024-01-04 09:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0127_alter_relatedcontentcta_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharesettings',
            name='hashtags',
            field=models.TextField(
                blank=True,
                help_text='Appends draft social media post when using the share page component. Write each tag in Pascal case and separate with a comma, for example: HashTagOne,HashTagTwo.',
                max_length=255,
                verbose_name='Hashtags',
            ),
        ),
    ]
