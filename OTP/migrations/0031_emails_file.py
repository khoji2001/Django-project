# Generated by Django 3.2.6 on 2021-09-19 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OTP', '0030_auto_20210919_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='emails',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='tass/', verbose_name='فایل'),
        ),
    ]
