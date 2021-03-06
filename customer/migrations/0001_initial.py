# Generated by Django 2.2 on 2020-06-08 18:40

import customer.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job', models.CharField(blank=True, max_length=30, verbose_name='شغل')),
                ('status', models.CharField(choices=[('0', 'درحال بررسی'), ('1', 'تایید شده'), ('2', 'رد شده')], default='0', max_length=1, verbose_name='وضعیت')),
                ('level', models.CharField(choices=[('0', 'مشخص نشده'), ('1', 'تا سقف ۸ میلیون تومان تسهیلات'), ('2', 'از ۸ تا سقف ۲۰ میلیون تومان تسهیلات'), ('3', 'از ۲۰ تا سقف ۳۰ میلیون تومان تسهیلات')], default='0', max_length=1, verbose_name='سطح تسهیلات')),
                ('estimate_income', models.IntegerField(default=0, verbose_name='حدود درآمد ماهانه')),
                ('postal_code', models.CharField(blank=True, default='', max_length=10, verbose_name='کد پستی')),
                ('credit_rank', models.TextField(blank=True, verbose_name='رتبه ی اعتباری')),
                ('organ_code', models.CharField(blank=True, default='', max_length=1, verbose_name='کد سازمان')),
            ],
            options={
                'verbose_name': 'متقاضی',
                'verbose_name_plural': 'متقاضیان',
            },
        ),
        migrations.CreateModel(
            name='Organ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30, verbose_name='عنوان')),
            ],
            options={
                'verbose_name': 'سازمان',
                'verbose_name_plural': 'سازمان ها',
            },
        ),
        migrations.CreateModel(
            name='surety',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=30, verbose_name='نام')),
                ('family_name', models.CharField(blank=True, default='', max_length=50, verbose_name='نام خانوادگی')),
                ('father_name', models.CharField(blank=True, default='', max_length=30, verbose_name='نام پدر')),
                ('melli_code', models.CharField(blank=True, default='', max_length=10, validators=[customer.models.validate_melli_code], verbose_name='کد ملی')),
                ('mobile_number', models.CharField(blank=True, default='', max_length=11, validators=[customer.models.validate_mobile_number], verbose_name='شماره همراه')),
                ('phone_number', models.CharField(blank=True, default='', max_length=11, validators=[customer.models.validate_phone_number], verbose_name='تلفن ثابت')),
                ('workplace_number', models.CharField(blank=True, default='', max_length=11, validators=[customer.models.validate_phone_number], verbose_name='تلفن محل کار')),
                ('postal_code', models.CharField(blank=True, default='', max_length=10, verbose_name='کد پستی')),
                ('job', models.CharField(blank=True, default='', max_length=30, verbose_name='شغل')),
                ('estimate_income', models.IntegerField(default=0, verbose_name='حدود درآمد ماهانه')),
                ('province', models.CharField(blank=True, default='', max_length=30, verbose_name='استان')),
                ('city', models.CharField(blank=True, default='', max_length=30, verbose_name='شهر')),
                ('address', models.CharField(blank=True, default='', max_length=100, verbose_name='نشانی')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.customer', verbose_name='مضمون عنه')),
            ],
            options={
                'verbose_name': 'ضامن',
                'verbose_name_plural': 'ضامن ها',
            },
        ),
        migrations.AddField(
            model_name='customer',
            name='organ',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer.Organ', verbose_name='سازمان معرف'),
        ),
    ]
