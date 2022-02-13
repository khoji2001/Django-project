# Generated by Django 3.2.6 on 2021-09-19 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OTP', '0028_alter_emails_email_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emails',
            name='email_type',
            field=models.CharField(choices=[('0', 'قرار ملاقات'), ('1', 'ارسال صندوق'), ('2', 'اکسل فروش ماهیانه'), ('3', 'تسویه قرارداد بااکسل'), ('4', 'متقاضی و فروشگاه'), ('5', 'تامین کننده جدید'), ('6', 'تسویه با جریمه'), ('7', 'اعتبار سنجی')], default='0', max_length=1, verbose_name='نوع ایمیل'),
        ),
    ]
