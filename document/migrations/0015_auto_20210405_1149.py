# Generated by Django 2.2 on 2021-04-05 07:19

from django.db import migrations, models
import document.models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0014_auto_20210404_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_document',
            name='credit_rate',
            field=models.FileField(blank=True, null=True, upload_to=document.models.customer_directory_path, verbose_name='رتبه اعتباری'),
        ),
        migrations.AlterField(
            model_name='customer_document',
            name='mellicard_front',
            field=models.FileField(blank=True, null=True, upload_to=document.models.customer_directory_path, verbose_name='روی کارت ملی'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='credit_rate',
            field=models.FileField(blank=True, null=True, upload_to=document.models.surety_directory_path, verbose_name='رتبه اعتباری'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='mellicard_front',
            field=models.FileField(blank=True, null=True, upload_to=document.models.surety_directory_path, verbose_name='روی کارت ملی'),
        ),
    ]
