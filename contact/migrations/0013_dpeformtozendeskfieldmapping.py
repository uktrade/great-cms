# Generated by Django 4.1.10 on 2023-11-07 16:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contact', '0012_auto_20230630_1626'),
    ]

    operations = [
        migrations.CreateModel(
            name='DPEFormToZendeskFieldMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dpe_form_field_id', models.CharField(max_length=255, null=True)),
                ('zendesk_field_id', models.CharField(max_length=255, null=True)),
                ('dpe_form_value_to_zendesk_field_value', models.JSONField(blank=True, null=True)),
            ],
        ),
    ]
