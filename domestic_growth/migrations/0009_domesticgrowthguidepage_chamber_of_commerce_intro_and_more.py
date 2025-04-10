# Generated by Django 4.2.19 on 2025-03-25 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('domestic_growth', '0008_merge_20250324_1742'),
    ]

    operations = [
        migrations.AddField(
            model_name='domesticgrowthguidepage',
            name='chamber_of_commerce_intro',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='domesticgrowthguidepage',
            name='primary_regional_support_intro_england',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='domesticgrowthguidepage',
            name='primary_regional_support_intro_ni',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='domesticgrowthguidepage',
            name='primary_regional_support_intro_scotland',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='domesticgrowthguidepage',
            name='primary_regional_support_intro_wales',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='domesticgrowthguidepage',
            name='primary_regional_support_title_england',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='domesticgrowthguidepage',
            name='primary_regional_support_title_ni',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='domesticgrowthguidepage',
            name='primary_regional_support_title_scotland',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='domesticgrowthguidepage',
            name='primary_regional_support_title_wales',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='domesticgrowthguidepage',
            name='trade_associations_intro',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='domesticgrowthguidepage',
            name='trade_associations_title',
            field=models.TextField(null=True),
        ),
    ]
