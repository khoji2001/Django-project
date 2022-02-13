# Generated by Django 3.0.7 on 2020-08-22 12:28

from django.db import migrations, models
import document.models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0005_auto_20200627_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_document',
            name='caccount_turnover',
            field=models.FileField(blank=True, null=True, upload_to=document.models.customer_directory_path, verbose_name='گردش حساب جاری'),
        ),
        migrations.AlterField(
            model_name='customer_document',
            name='complemental',
            field=models.FileField(blank=True, null=True, upload_to=document.models.customer_directory_path, verbose_name='مدارک تکمیلی'),
        ),
        migrations.AlterField(
            model_name='customer_document',
            name='employment_certification',
            field=models.FileField(blank=True, null=True, upload_to=document.models.customer_directory_path, verbose_name='گواهی اشتغال-جواز کسب'),
        ),
        migrations.AlterField(
            model_name='customer_document',
            name='house_evidence',
            field=models.FileField(blank=True, null=True, upload_to=document.models.customer_directory_path, verbose_name='مدرک سکونت'),
        ),
        migrations.AlterField(
            model_name='customer_document',
            name='oaccount_turnover',
            field=models.FileField(blank=True, null=True, upload_to=document.models.customer_directory_path, verbose_name=' گردش حساب اصلی یا فیش حقوقی مهردار'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='caccount_turnover',
            field=models.FileField(blank=True, null=True, upload_to=document.models.surety_directory_path, verbose_name='گردش حساب جاری'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='complemental',
            field=models.FileField(blank=True, null=True, upload_to=document.models.surety_directory_path, verbose_name='مدارک تکمیلی'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='employment_certification',
            field=models.FileField(blank=True, null=True, upload_to=document.models.surety_directory_path, verbose_name='گواهی اشتغال -جواز کسب'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='house_evidence',
            field=models.FileField(blank=True, null=True, upload_to=document.models.surety_directory_path, verbose_name='مدرک سکونت'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='oaccount_turnover',
            field=models.FileField(blank=True, null=True, upload_to=document.models.surety_directory_path, verbose_name=' گردش حساب اصلی یا فیش حقوقی مهردار'),
        ),
    ]
