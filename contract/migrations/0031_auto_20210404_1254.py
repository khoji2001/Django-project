# Generated by Django 2.2 on 2021-04-04 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0030_auto_20210403_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='status',
            field=models.CharField(choices=[('0', 'تایید دریافت پیش پرداخت'), ('1', 'درحال عقد قرارداد'), ('2', ' تایید قرارداد و ارسال کالا'), ('21', 'ارسال به صندوق'), ('3', 'تسویه با فروشگاه'), ('4', 'پرداخت اقساط توسط متقاضی'), ('5', 'تسویه متقاضی و تحویل مدارک'), ('7', 'انصراف متقاضی')], default='0', max_length=2, verbose_name='وضعیت قراردادی'),
        ),
    ]
