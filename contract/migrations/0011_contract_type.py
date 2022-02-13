# Generated by Django 3.0.7 on 2020-09-24 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0010_auto_20200912_1713'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='Type',
            field=models.CharField(choices=[('0', 'نوع ۱( محاسبات طبق اکسل)'), ('1', 'نوع ۲(محاسبات irr)')], default='0', max_length=1, verbose_name='نوع قرارداد'),
        ),
    ]