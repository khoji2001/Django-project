# Generated by Django 2.2 on 2021-05-19 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0036_merge_20210501_1157'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ['date'], 'verbose_name': 'پرداخت', 'verbose_name_plural': 'پرداخت ها'},
        ),
    ]
