# Generated by Django 2.2 on 2021-04-05 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OTP', '0012_auto_20210404_1226'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagetext',
            name='good_payer',
            field=models.TextField(default='متقاضی محترم فرامیران\nباسلام\nقسط {0} ماه شما دریافت شده است\nبا تشکر از خوش حسابی {1}\n\nفرامیران', verbose_name='پیامک خوش حسابی'),
        ),
    ]
