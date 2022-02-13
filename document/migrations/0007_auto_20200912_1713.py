# Generated by Django 3.0.7 on 2020-09-12 12:43

from django.db import migrations, models
import document.models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0006_auto_20200822_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_document',
            name='identity_description',
            field=models.FileField(blank=True, null=True, upload_to=document.models.customer_directory_path, verbose_name='توضیحات شناسنامه'),
        ),
        migrations.AlterField(
            model_name='customer_document',
            name='identity_firstpage',
            field=models.FileField(blank=True, null=True, upload_to=document.models.customer_directory_path, verbose_name='صفحه اول شناسنامه'),
        ),
        migrations.AlterField(
            model_name='customer_document',
            name='mellicard_behind',
            field=models.FileField(upload_to=document.models.customer_directory_path, verbose_name='پشت کارت ملی'),
        ),
        migrations.AlterField(
            model_name='customer_document',
            name='mellicard_front',
            field=models.FileField(upload_to=document.models.customer_directory_path, verbose_name='روی کارت ملی'),
        ),
        migrations.AlterField(
            model_name='customer_document',
            name='receipt_of_deposit',
            field=models.FileField(blank=True, null=True, upload_to=document.models.customer_directory_path, verbose_name='رسید هزینه ی اعتبارسنجی'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='identity_description',
            field=models.FileField(blank=True, null=True, upload_to=document.models.surety_directory_path, verbose_name='توضیحات شناسنامه'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='identity_firstpage',
            field=models.FileField(blank=True, null=True, upload_to=document.models.surety_directory_path, verbose_name='صفحه اول شناسنامه'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='mellicard_behind',
            field=models.FileField(upload_to=document.models.surety_directory_path, verbose_name='پشت کارت ملی'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='mellicard_front',
            field=models.FileField(upload_to=document.models.surety_directory_path, verbose_name='روی کارت ملی'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='receipt_of_deposit',
            field=models.FileField(blank=True, null=True, upload_to=document.models.surety_directory_path, verbose_name='رسید هزینه ی اعتبارسنجی'),
        ),
    ]