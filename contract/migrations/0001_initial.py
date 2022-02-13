# Generated by Django 2.2 on 2020-06-08 18:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sign_date', models.DateField(blank=True, null=True, verbose_name='تاریخ امضا')),
                ('invoice_date', models.DateField(blank=True, null=True, verbose_name='تاریخ فاکتور')),
                ('invoice_number', models.CharField(default='', max_length=20, verbose_name='شماره فاکتور')),
                ('description', models.TextField(blank=True, default='', verbose_name='شرح فاکتور')),
                ('clearing_date', models.DateField(blank=True, null=True, verbose_name='تاریخ تسویه با فروشگاه')),
                ('net_amount', models.PositiveIntegerField(null=True, verbose_name='مبلغ فاکتور')),
                ('number_of_instalment', models.IntegerField(default=12, verbose_name='تعداد اقساط')),
                ('additional_costs', models.IntegerField(blank=True, verbose_name='هزینه ی اضافی')),
                ('downpayment', models.IntegerField(blank=True, verbose_name='پیش پرداخت')),
                ('status', models.CharField(choices=[('0', 'تأیید نشده'), ('1', ' تایید دریافت پیش پرداخت درحال عقد قرارداد'), ('2', ' تایید قرارداد و ارسال کالا'), ('3', 'تسویه با فروشگاه'), ('4', 'پرداخت اقساط توسط متقاضی'), ('5', 'تسویه نهایی اقساط'), ('6', 'تحویل مدارک به متقاضی'), ('7', 'انصراف متقاضی')], default='0', max_length=1, verbose_name='وضعیت')),
                ('customer_fullname', models.CharField(max_length=50, verbose_name='نام کامل متقاضی')),
                ('supplier_name', models.CharField(max_length=50, verbose_name='نام فروشگاه')),
                ('contract_id', models.CharField(max_length=20, null=True, unique=True, verbose_name='شماره قرارداد')),
                ('financial_source_rate', models.FloatField(blank=True, verbose_name='تسهیلات خالص')),
                ('warranty_gain_rate', models.FloatField(blank=True, verbose_name='کارمزد صدور ضمانت نامه')),
                ('share_rate', models.FloatField(blank=True, verbose_name='  سهم شرکت از ضمانت نامه')),
                ('company_gain_rate', models.FloatField(blank=True, verbose_name='کارمزد شرکت')),
                ('investor_gain_rate', models.FloatField(blank=True, verbose_name='کارمزد بازاریاب')),
                ('discount', models.FloatField(blank=True, verbose_name='تخفیف')),
                ('vcc_number', models.CharField(default='', max_length=16, verbose_name='شماره کارت')),
            ],
            options={
                'verbose_name': 'قرارداد',
                'verbose_name_plural': 'قراردادها',
            },
        ),
        migrations.CreateModel(
            name='vcc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=16, unique=True, verbose_name='شماره کارت')),
                ('amount', models.IntegerField(default=0, verbose_name='موجودی')),
            ],
            options={
                'verbose_name': 'کارت بانکی',
                'verbose_name_plural': 'کارت بانکی',
            },
        ),
        migrations.CreateModel(
            name='payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(verbose_name='مبلغ')),
                ('date', models.DateField(verbose_name='تاریخ')),
                ('voucher_id', models.CharField(max_length=40, unique=True, verbose_name='شماره سند بانکی')),
                ('VCC', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contract.vcc', verbose_name='شماره کارت')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contract.contract', verbose_name='قرارداد')),
            ],
            options={
                'verbose_name': 'پرداخت',
                'verbose_name_plural': 'پرداخت ها',
            },
        ),
    ]