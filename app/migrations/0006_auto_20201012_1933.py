# Generated by Django 3.1 on 2020-10-12 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20201012_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customizemodulename',
            name='customize_name',
            field=models.IntegerField(blank=True, choices=[(1, 'Contact'), (2, 'Product'), (3, 'Credit Note'), (4, 'Purhase Order'), (5, 'Invoice'), (6, 'Expense'), (7, 'Purchase Entry'), (8, 'Debit Note'), (9, 'quotation')], db_index=True, null=True),
        ),
        migrations.CreateModel(
            name='CustomizeQuotationView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quotation_number', models.IntegerField(blank=True, choices=[(1, 'YES'), (0, 'NO')], db_index=True, default=0, null=True)),
                ('quotation_customer', models.IntegerField(blank=True, choices=[(1, 'YES'), (0, 'NO')], db_index=True, default=0, null=True)),
                ('quotation_date', models.IntegerField(blank=True, choices=[(1, 'YES'), (0, 'NO')], db_index=True, default=0, null=True)),
                ('quotation_expire_date', models.IntegerField(blank=True, choices=[(1, 'YES'), (0, 'NO')], db_index=True, default=0, null=True)),
                ('quotation_amount', models.IntegerField(blank=True, choices=[(1, 'YES'), (0, 'NO')], db_index=True, default=0, null=True)),
                ('customize_view_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.customizemodulename')),
            ],
        ),
    ]
