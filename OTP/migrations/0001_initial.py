# Generated by Django 2.2 on 2020-06-08 18:40

import OTP.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MobileCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_created=True, auto_now_add=True)),
                ('verified', models.BooleanField(auto_created=True, default=False, verbose_name='تایید شده')),
                ('token', models.IntegerField(auto_created=True, default=OTP.models.create_token, unique=True, verbose_name='کد عضویت')),
                ('mobile_number', models.CharField(max_length=11, validators=[OTP.models.validate_mobile_number], verbose_name='شماره همراه')),
            ],
            options={
                'verbose_name': 'کد عضویت',
                'verbose_name_plural': 'کد عضویت\u200cها',
            },
        ),
    ]
