# Generated by Django 2.2 on 2021-01-04 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0016_auto_20201221_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='estimate_income',
            field=models.IntegerField(default=0, help_text='میلیون ریال', verbose_name='حدود درآمد ماهانه'),
        ),
        migrations.AlterField(
            model_name='surety',
            name='estimate_income',
            field=models.IntegerField(default=0, help_text='میلیون ریال', verbose_name='حدود درآمد ماهانه'),
        ),
    ]
