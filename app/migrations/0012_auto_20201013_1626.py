# Generated by Django 3.1 on 2020-10-13 10:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20201013_1611'),
    ]

    operations = [
        migrations.RenameField(
            model_name='invoicemodel',
            old_name='inovice_over_due_count',
            new_name='invoice_over_due_count',
        ),
    ]