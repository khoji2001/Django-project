# Generated by Django 3.0.7 on 2020-11-09 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0011_contract_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='additional_costs',
            field=models.IntegerField(blank=True, help_text='ریال', verbose_name='هزینه ی اضافی'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='downpayment',
            field=models.IntegerField(blank=True, help_text='ریال', verbose_name='پیش پرداخت'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='net_amount',
            field=models.PositiveIntegerField(help_text='ریال', verbose_name='مبلغ فاکتور'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.IntegerField(help_text='ریال', verbose_name='مبلغ'),
        ),
    ]
