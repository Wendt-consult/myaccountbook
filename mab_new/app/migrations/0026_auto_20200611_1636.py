# Generated by Django 3.0.7 on 2020-06-11 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_customizepurchaseview_purchase_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contacts',
            name='organization_type',
            field=models.IntegerField(choices=[(1, 'Individual'), (2, 'Proprietorship'), (4, 'Partnership'), (5, 'Trust'), (6, 'Private Limited'), (7, 'Public Limited'), (8, 'Overseas Organisation'), (9, 'Government Organisation')], db_index=True, default=1),
        ),
        migrations.AlterField(
            model_name='customizemodulename',
            name='customize_name',
            field=models.IntegerField(blank=True, choices=[(1, 'Contact'), (2, 'Product'), (3, 'Credit Note'), (4, 'Purhase Order'), (5, 'Invoice'), (6, 'Expense')], db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='organisations',
            name='organisation_type',
            field=models.IntegerField(choices=[(1, 'Individual'), (2, 'Proprietorship'), (4, 'Partnership'), (5, 'Trust'), (6, 'Private Limited'), (7, 'Public Limited'), (8, 'Overseas Organisation'), (9, 'Government Organisation')], db_index=True, default=1),
        ),
    ]