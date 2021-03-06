# Generated by Django 2.2 on 2021-10-02 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_user_first_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='description',
            field=models.TextField(blank=True, verbose_name='توضیحات کاربر'),
        ),
        migrations.AlterField(
            model_name='user',
            name='education',
            field=models.CharField(choices=[('0', 'بی سواد'), ('1', 'ابتدایی'), ('2', 'سیکل'), ('3', 'دیپلم'), ('4', 'کاردانی'), ('5', 'کارشناسی'), ('6', 'کارشناسی ارشد'), ('7', 'دکتری'), ('8', 'علوم پزشکی'), ('9', 'تحصیلات حوزوی')], default='3', max_length=1, verbose_name='سطح تحصیلات'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='first name'),
        ),
    ]
