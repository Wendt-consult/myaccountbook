# Generated by Django 3.1 on 2020-10-13 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_quotationmodel_quotation_pay_terms'),
    ]

    operations = [
        migrations.AddField(
            model_name='quotationmodel',
            name='is_invoice_creted',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]