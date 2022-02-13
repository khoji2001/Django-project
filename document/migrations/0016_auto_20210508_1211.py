# Generated by Django 2.2 on 2021-05-08 07:41

from django.db import migrations, models
import document.models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0015_auto_20210405_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_document',
            name='employment_certification',
            field=models.FileField(blank=True, null=True, upload_to=document.models.customer_directory_path, verbose_name='گواهی اشتغال یا جواز کسب یا لیست بیمه'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='employment_certification',
            field=models.FileField(blank=True, null=True, upload_to=document.models.surety_directory_path, verbose_name='گواهی اشتغال یا جواز کسب یا لیست بیمه'),
        ),
    ]