# Generated by Django 2.2 on 2021-05-10 08:11

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20210421_1100'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='melli_code',
            field=models.CharField(blank=True, max_length=10, unique=True, validators=[users.models.validate_melli_code], verbose_name='کد ملی'),
        ),
    ]
