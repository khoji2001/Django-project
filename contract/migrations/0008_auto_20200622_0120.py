# Generated by Django 3.0.7 on 2020-06-21 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0007_auto_20200620_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='invoice_number',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='شماره فاکتور'),
        ),
    ]