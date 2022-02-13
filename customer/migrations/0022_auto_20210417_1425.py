# Generated by Django 2.2 on 2021-04-17 09:55

import customer.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0021_auto_20210404_1501'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='job_address',
            field=models.TextField(blank=True, default='', verbose_name='نشانی محل کار'),
        ),
        migrations.AddField(
            model_name='customer',
            name='job_phone_number',
            field=models.CharField(blank=True, default='', max_length=11, verbose_name='شماره تماس محل کار'),
        ),
        migrations.AddField(
            model_name='customer',
            name='job_workplace',
            field=models.CharField(blank=True, max_length=50, verbose_name='محل شغل'),
        ),
        migrations.AddField(
            model_name='customer',
            name='marital_status',
            field=models.CharField(choices=[('0', 'مجرد'), ('1', 'متاهل'), ('2', 'سرپرست خانوار')], default='0', max_length=1, verbose_name='وضعیت تاهل'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='job',
            field=models.CharField(blank=True, max_length=30, verbose_name='عنوان شغلی'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='job_class',
            field=models.CharField(choices=[('0', 'دولتی'), ('1', 'آزاد'), ('2', 'مستمری بگیر'), ('3', 'خصوصی'), ('4', 'نظامی'), ('5', 'بازنشسته')], default='0', max_length=1, verbose_name='حوزه شغلی'),
        ),
        migrations.AlterField(
            model_name='surety',
            name='job_class',
            field=models.CharField(choices=[('0', 'دولتی'), ('1', 'آزاد'), ('2', 'مستمری بگیر'), ('3', 'خصوصی'), ('4', 'نظامی'), ('5', 'بازنشسته')], default='0', max_length=1, verbose_name='حوزه شغلی'),
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('Type', models.CharField(choices=[('0', 'مادر'), ('1', 'پدر'), ('2', 'برادر'), ('3', 'خواهر'), ('4', 'همسر')], default='0', max_length=1, verbose_name='نسبت با متقاضی')),
                ('mobile_number', models.CharField(max_length=11, unique=True, validators=[customer.models.validate_mobile_number], verbose_name='شماره همراه')),
                ('melli_code', models.CharField(blank=True, max_length=10, validators=[customer.models.validate_melli_code], verbose_name='کد ملی')),
                ('phone_number', models.CharField(blank=True, default='', max_length=11, verbose_name='تلفن ثابت')),
                ('phone_number_description', models.CharField(max_length=20, verbose_name='عنوان تلفن ثابت')),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='customer.customer', verbose_name='متقاضی')),
            ],
        ),
    ]
