# Generated by Django 2.2 on 2021-05-11 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0027_auto_20210428_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='credit_rank',
            field=models.CharField(blank=True, default='', max_length=1000, verbose_name='شرح وضعیت'),
        ),
    ]
