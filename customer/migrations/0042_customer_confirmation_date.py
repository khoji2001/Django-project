# Generated by Django 2.2 on 2021-08-15 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0041_customer_surety_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='confirmation_date',
            field=models.DateField(blank=True, null=True, verbose_name='تاریخ تایید'),
        ),
    ]
