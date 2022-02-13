# Generated by Django 2.2 on 2021-06-07 07:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0036_auto_20210602_1503'),
        ('contract', '0037_auto_20210519_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractsuretys',
            name='cust',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='customer.customer', verbose_name='ضامن'),
        ),
    ]
