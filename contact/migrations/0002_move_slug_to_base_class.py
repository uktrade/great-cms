# Generated by Django 2.2.19 on 2021-03-17 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactsuccesssnippet',
            name='slug',
            field=models.CharField(
                help_text='Select the use-case for this snippet from a fixed list of choices',
                max_length=255,
                unique=True,
                verbose_name='Purpose',
            ),
        ),
    ]
