# Generated by Django 3.2.6 on 2021-09-14 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OTP', '0017_remove_messagetext_check_appointment'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagetext',
            name='mulct_pay',
            field=models.TextField(default='{0}متقاضی محترم فرامیران\nبا سلام\nلطفا جریمه خود را پرداخت کنید\nمیزان جریمه شما:{1}\nنشانی دفتر شرکت:\nجنت آباد جنوبی، خیابان چهارباغ شرقی، ۱۶ متری شمالی یکم، کوچه آذرشب، پلاک ۳۸/۱ واحد ۱۲\n', verbose_name='پیامک پرداخت جریمه '),
        ),
    ]
