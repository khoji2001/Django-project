# Generated by Django 3.2.6 on 2021-09-18 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OTP', '0025_auto_20210918_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emails',
            name='ET',
            field=models.TextField(blank=True, null=True, verbose_name='متن ایمیل'),
        ),
        migrations.AlterField(
            model_name='emails',
            name='ST',
            field=models.TextField(blank=True, null=True, verbose_name='عنوان ایمل'),
        ),
        migrations.AlterField(
            model_name='emails',
            name='TO',
            field=models.TextField(blank=True, help_text='برای جداسازی از , استفاده کنید', null=True, verbose_name='دریافت کنندگان'),
        ),
        migrations.AlterField(
            model_name='emails',
            name='bcc',
            field=models.TextField(blank=True, null=True, verbose_name='رونوشت مخفی'),
        ),
        migrations.AlterField(
            model_name='emails',
            name='cc',
            field=models.TextField(blank=True, null=True, verbose_name='رونوشت'),
        ),
    ]
