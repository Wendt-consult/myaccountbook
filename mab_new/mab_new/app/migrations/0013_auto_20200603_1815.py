# Generated by Django 3.0.6 on 2020-06-03 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20200602_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='advacne_payemtn_method',
            field=models.IntegerField(blank=True, choices=[(1, 'Cash'), (2, 'Card'), (3, 'Cheque'), (4, 'Demand Draft'), (5, 'Net Banking')], db_index=True, default=1, null=True),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='advance_payment_date',
            field=models.DateField(blank=True, db_index=True, null=True),
        ),
    ]