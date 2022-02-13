# Generated by Django 2.2 on 2021-08-23 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OTP', '0015_auto_20210823_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagetext',
            name='check_appointment_first',
            field=models.TextField(default='متقاضی محترم فرامیران\nبا سلام\nنوبت شما برای عقد قرارداد تسهیلات خرید اقساطی در روز {0} ساعت {1} معین شده است. در صورت عدم مراجعه به منزله انصراف از خرید بوده و مشمول دریافت جریمه از شما است.\nنشانی دفتر شرکت:\nجنت آباد جنوبی، خیابان چهارباغ شرقی، ۱۶ متری شمالی یکم، کوچه آذرشب، پلاک ۳۸/۱ واحد ۱۲\n', verbose_name='پیامک اول قرارملاقات'),
        ),
        migrations.AlterField(
            model_name='messagetext',
            name='check_appointment_second',
            field=models.TextField(default='\nهمراه داشتن مدارک ذیل (برای خریدار و ضامن/ضامنین) الزامی است\n1- اصل و کپی کارت ملی(پشت و رو) و شناسنامه (تمامی صفحات) روی برگه A4\n2- گواهی کد پستی محل سکونت به همراه کپی اجاره نامه یا سند مالکیت روی برگه A4\n3- گردش حساب سه ماهه هر دو حساب اصلی(حقوقی) و جاری. (گردش حساب باید به صورت خروجی PDF از اینترنت بانک یا به صورت نسخه فیزیکی از بانک تهیه شود)\n4- دسته چک صیاد صادره از شهر تهران\n5- پیش فاکتور مهردار فروشگاه\n', verbose_name='پیامک دوم قرارملاقات'),
        ),
    ]
