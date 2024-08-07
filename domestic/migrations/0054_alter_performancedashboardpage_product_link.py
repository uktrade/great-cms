# Generated by Django 4.2.7 on 2024-02-12 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domestic', '0053_alter_articlepage_article_body'),
    ]

    operations = [
        migrations.AlterField(
            model_name='performancedashboardpage',
            name='product_link',
            field=models.CharField(
                choices=[
                    ('https://www.great.gov.uk', 'Great.gov.uk'),
                    ('https://www.great.gov.uk/export-opportunities', 'Export Opportunities'),
                    ('https://www.great.gov.uk/find-a-buyer', 'Business Profiles'),
                    ('https://invest.great.gov.uk', 'Invest in Great Britain'),
                ],
                help_text='The slug and page heading are inferred from the product link. The first option should be the first performance dashboard page and the rest should be used for CHILDREN of that main dashboard.',
                max_length=255,
                unique=True,
            ),
        ),
    ]
