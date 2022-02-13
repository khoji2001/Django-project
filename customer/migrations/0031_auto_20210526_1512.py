# Generated by Django 2.2 on 2021-05-26 10:42

import customer.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0030_merge_20210511_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='mobile_number',
            field=models.CharField(max_length=11, validators=[customer.models.validate_mobile_number], verbose_name='شماره همراه'),
        ),
        migrations.AlterField(
            model_name='personalhome',
            name='mobile_number',
            field=models.CharField(max_length=11, validators=[customer.models.validate_mobile_number], verbose_name='شماره همراه'),
        ),
        migrations.AlterField(
            model_name='rentalhome',
            name='mobile_number',
            field=models.CharField(max_length=11, validators=[customer.models.validate_mobile_number], verbose_name='شماره همراه'),
        ),
    ]