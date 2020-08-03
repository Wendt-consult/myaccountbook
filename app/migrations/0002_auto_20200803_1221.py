# Generated by Django 3.0.8 on 2020-08-03 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditnode',
            name='creditnote_org_gst_num',
            field=models.CharField(blank=True, db_index=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='creditnode',
            name='creditnote_org_gst_state',
            field=models.CharField(blank=True, db_index=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='creditnode',
            name='creditnote_org_gst_type',
            field=models.CharField(blank=True, db_index=True, max_length=2, null=True),
        ),
    ]
