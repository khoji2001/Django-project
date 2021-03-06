# Generated by Django 3.0.7 on 2020-11-09 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OTP', '0004_auto_20201109_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagetext',
            name='check_appointment',
            field=models.TextField(default='با سلام\nمتقاضی محترم، زمان مراجعه شما روز {0} ساعت {1} می باشد. لطفا با در دست داشتن اصل شناسنامه و کارت ملی و همچنین همراه داشتن چک صیاد به آدرس دفتر مراجعه نمایید.\n\nموقعیت شرکت توسعه مبادلات:\nجنت آباد جنوبی، خیابان چهارباغ شرقی، ۱۶ متری شمالی یکم، کوچه آذرشب، پلاک ۳۸/۱ واحد ۱۲\nhttps://goo.gl/maps/WFUk6g7MJk82 :لینک', verbose_name='پیامک یادآوری اقساط'),
        ),
        migrations.AlterField(
            model_name='messagetext',
            name='notify_debit',
            field=models.TextField(default='با سلام\nمتقاضی محترم، قسط خرید لوام خانگی ایرانی شما معوق شده است؛ خواهشمند است، در اسرع وقت نسبت به تسویه آن اقدام و مراتب را به شماره واتس اپ یا تلگرام ۰۹۳۷۴۷۸۸۶۳۴ اطلاع دهید.\n\nاطلاعات اقساط شما:\nسررسید: {0} هر ماه\nشماره کارت اختصاصی شما: {1}\nمبلغ هر قسط: {2} ریال\n\nبا تشکر\nفرامیران- مجری ارائه تسهیلات فروش اقساطی محصولات ایرانی', verbose_name='پیامک معوقه اقساط'),
        ),
        migrations.AlterField(
            model_name='messagetext',
            name='reject_customer',
            field=models.TextField(default='باسلام\nمتقاضی محترم پرونده شما تایید نشد. لطفا با مراجعه به حساب کاربری خود نسبت به دلیل عدم تایید اطلاع یابید.\n\nباتشکر\nفرامیران- مجری ارائه تسهیلات فروش اقساطی محصولات ایرانی', verbose_name='پیامک رد اعتبار'),
        ),
        migrations.AlterField(
            model_name='messagetext',
            name='verify_contract',
            field=models.TextField(default='باسلام\nمتقاضی محترم، پرونده شما تایید شد. لطفا برای دریافت و ترخیص کالا به فروشگاه مراجعه نمایید.\n\nباتشکر\nفرامیران- مجری ارائه تسهیلات فروش اقساطی محصولات ایرانی', verbose_name='پیامک تحویل کالا'),
        ),
        migrations.AlterField(
            model_name='messagetext',
            name='verify_customer',
            field=models.TextField(default='باسلام\nمتقاضی محترم پرونده شما تایید گردید. لطفا با مراجعه به فروشگاه برای تعیین زمان و دریافت پیش فاکتور اقدام نمایید.\n\nباتشکر\nفرامیران- مجری ارائه تسهیلات فروش اقساطی محصولات ایرانی', verbose_name='پیامک تایید اعتبار'),
        ),
    ]
