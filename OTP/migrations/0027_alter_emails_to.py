# Generated by Django 3.2.6 on 2021-09-18 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OTP', '0026_auto_20210918_1218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emails',
            name='TO',
            field=models.TextField(blank=True, help_text='برای جداسازی از , استفاده کنید', null=True, verbose_name='گیرندگان'),
        ),
    ]
