# Generated by Django 3.0.7 on 2020-06-22 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organisations',
            name='invoice_note',
            field=models.CharField(blank=True, db_index=True, max_length=400, null=True),
        ),
        migrations.AddField(
            model_name='organisations',
            name='invoice_terms_and_condition',
            field=models.CharField(blank=True, db_index=True, max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name='user_tax_details',
            name='bills_terms',
            field=models.IntegerField(blank=True, choices=[(1, 'Net 30'), (2, 'Net 45'), (3, 'Net 60'), (4, 'Due on Receipt'), (5, 'Due end of next month'), (6, 'Due end of the month')], db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='user_tax_details',
            name='invoice_terms',
            field=models.IntegerField(blank=True, choices=[(1, 'Net 30'), (2, 'Net 45'), (3, 'Net 60'), (4, 'Due on Receipt'), (5, 'Due end of next month'), (6, 'Due end of the month')], db_index=True, null=True),
        ),
    ]