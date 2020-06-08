# Generated by Django 3.0.4 on 2020-06-01 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20200601_1015'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='delivery_state',
            field=models.CharField(blank=True, db_index=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='save_type',
            field=models.IntegerField(choices=[(1, 'save_send'), (2, 'save_close'), (3, 'save_draft'), (4, 'save_print')], db_index=True, default=2),
        ),
        migrations.AlterField(
            model_name='user_tax_details',
            name='gst_reg_type',
            field=models.IntegerField(blank=True, choices=[(0, 'Not Applicable'), (1, 'GST Registered-Regular'), (2, 'GST Registered-Composition'), (3, 'GST Unregistered'), (4, 'Consumer'), (5, 'Overseas'), (6, 'SEZ'), (7, 'Deemed Exports -EOU’s, STP’s , EHTP’s etc'), (8, 'Composite GST')], db_index=True, default=0, null=True),
        ),
    ]