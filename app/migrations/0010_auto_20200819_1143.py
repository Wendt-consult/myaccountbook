# Generated by Django 3.1 on 2020-08-19 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20200818_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsmodel',
            name='product_type',
            field=models.IntegerField(choices=[(0, 'GOODS'), (1, 'SERVICES'), (2, 'BUNDLE')], db_index=True, default=0),
        ),
    ]
