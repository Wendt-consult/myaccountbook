# Generated by Django 3.0.4 on 2020-05-30 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_user_address_details_default_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_address_details',
            name='address_tag',
            field=models.TextField(blank=True, null=True),
        ),
    ]
