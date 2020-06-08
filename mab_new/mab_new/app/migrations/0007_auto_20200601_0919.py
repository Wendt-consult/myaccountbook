# Generated by Django 3.0.4 on 2020-06-01 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_user_address_details_address_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_address_details',
            name='organisation_cin',
            field=models.CharField(blank=True, db_index=True, max_length=21, null=True),
        ),
        migrations.AddField(
            model_name='user_address_details',
            name='organisation_pan',
            field=models.CharField(blank=True, db_index=True, max_length=10, null=True),
        ),
    ]
