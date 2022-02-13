# Generated by Django 2.2 on 2020-12-23 11:56

from django.db import migrations, models
import document.models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0010_auto_20201111_1125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract_document',
            name='customer_check',
            field=models.FileField(blank=True, null=True, upload_to=document.models.contract_directory_path, verbose_name='چک متقاضی'),
        ),
        migrations.AlterField(
            model_name='contract_document',
            name='downpayment_receipt',
            field=models.FileField(blank=True, null=True, upload_to=document.models.contract_directory_path, verbose_name='فیش واریز پیش پرداخت'),
        ),
        migrations.AlterField(
            model_name='contract_document',
            name='final_invoice',
            field=models.FileField(blank=True, null=True, upload_to=document.models.contract_directory_path, verbose_name='فاکتور نهایی'),
        ),
        migrations.AlterField(
            model_name='contract_document',
            name='pre_invoice',
            field=models.FileField(blank=True, null=True, upload_to=document.models.contract_directory_path, verbose_name='پیش فاکتور'),
        ),
        migrations.AlterField(
            model_name='contract_document',
            name='signed_contract',
            field=models.FileField(blank=True, null=True, upload_to=document.models.contract_directory_path, verbose_name='قرارداد امضا شده'),
        ),
        migrations.AlterField(
            model_name='contract_document',
            name='surety_check1',
            field=models.FileField(blank=True, null=True, upload_to=document.models.contract_directory_path, verbose_name='چک ضامن۱'),
        ),
        migrations.AlterField(
            model_name='contract_document',
            name='surety_check2',
            field=models.FileField(blank=True, null=True, upload_to=document.models.contract_directory_path, verbose_name='چک ضامن۲'),
        ),
    ]
