# Generated by Django 2.2.18 on 2021-02-17 13:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0057_auto_20210215_1204'),
    ]

    operations = [
        migrations.RenameField(
            model_name='casestudyscoringsettings',
            old_name='other_topics_tags',
            new_name='other_topic_tags',
        ),
    ]
