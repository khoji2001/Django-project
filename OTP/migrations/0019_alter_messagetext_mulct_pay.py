# Generated by Django 3.2.6 on 2021-09-14 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OTP', '0018_messagetext_mulct_pay'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagetext',
            name='mulct_pay',
            field=models.TextField(default='متقاضی محترم فرامیران\n{0}\nبا سلام\nلطفا جریمه خود را پرداخت کنید\nمیزان جریمه شما:{1}\nنشانی دفتر شرکت:\nجنت آباد جنوبی، خیابان چهارباغ شرقی، ۱۶ متری شمالی یکم، کوچه آذرشب، پلاک ۳۸/۱ واحد ۱۲\n', verbose_name='پیامک پرداخت جریمه '),
        ),
    ]
