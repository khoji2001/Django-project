# Generated by Django 3.0.7 on 2020-11-10 09:46

from django.db import migrations, models
import document.models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0008_auto_20201012_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer_document',
            name='credit_rate',
            field=models.FileField(upload_to=document.models.customer_directory_path, verbose_name='رتبه اعتباری'),
        ),
        migrations.AlterField(
            model_name='surety_document',
            name='credit_rate',
            field=models.FileField(upload_to=document.models.surety_directory_path, verbose_name='رتبه اعتباری'),
        ),
    ]
