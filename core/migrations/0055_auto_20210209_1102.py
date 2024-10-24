# Generated by Django 2.2.18 on 2021-02-09 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0054_casestudyscoringsettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='casestudyscoringsettings',
            name='no_country',
        ),
        migrations.RemoveField(
            model_name='casestudyscoringsettings',
            name='no_product',
        ),
        migrations.AddField(
            model_name='casestudyscoringsettings',
            name='other_module_tags',
            field=models.DecimalField(
                decimal_places=3,
                default=-0.5,
                help_text='This is the score we deduct for a case study should it have an association at this level in our information architecture',
                max_digits=5,
            ),
        ),
        migrations.AddField(
            model_name='casestudyscoringsettings',
            name='other_topics_tags',
            field=models.DecimalField(
                decimal_places=3,
                default=-0.25,
                help_text='This is the score we deduct for a case study should it have an association at this level in our information architecture',
                max_digits=5,
            ),
        ),
        migrations.AlterField(
            model_name='casestudyscoringsettings',
            name='other_lesson_tags',
            field=models.DecimalField(
                decimal_places=3,
                default=-0.1,
                help_text='This is the score we deduct for a case study should it have an association at this level in our information architecture',
                max_digits=5,
            ),
        ),
    ]
