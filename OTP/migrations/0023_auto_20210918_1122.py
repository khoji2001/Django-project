# Generated by Django 3.2.6 on 2021-09-18 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OTP', '0022_emails_et_appointment'),
    ]

    operations = [
        migrations.AddField(
            model_name='emails',
            name='ADMIN_EMAILS',
            field=models.TextField(default=' a.khoji2001@gmail.com , abolfazlkhojasteh2001@gmail.com', verbose_name='ایمیل ادمین ها'),
        ),
        migrations.AddField(
            model_name='emails',
            name='ST_appointment',
            field=models.TextField(default='قرارملاقات با {customer}', verbose_name='موضوع ایمیل قرار ملاقات'),
        ),
    ]
