# Generated by Django 2.2 on 2021-05-10 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0028_auto_20210508_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='cust_description',
            field=models.TextField(blank=True, verbose_name=' توضیحات متقاضی'),
        ),
    ]
