# Generated by Django 2.2 on 2020-06-16 14:50

from django.db import migrations, models
import document.models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0003_auto_20200616_1717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract_document',
            name='surety_check1',
            field=models.ImageField(blank=True, null=True, upload_to=document.models.contract_directory_path, verbose_name='چک ضامن۱'),
        ),
    ]
