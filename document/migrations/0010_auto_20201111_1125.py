# Generated by Django 3.0.7 on 2020-11-11 07:55

from django.db import migrations, models
import document.models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0009_auto_20201110_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract_document',
            name='customer_check',
            field=models.ImageField(blank=True, null=True, upload_to=document.models.contract_directory_path, verbose_name='چک متقاضی'),
        ),
        migrations.AlterField(
            model_name='contract_document',
            name='signed_contract',
            field=models.ImageField(blank=True, null=True, upload_to=document.models.contract_directory_path, verbose_name='قرارداد امضا شده'),
        ),
    ]
