# Generated by Django 2.2 on 2021-08-23 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0044_auto_20210724_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='contract_permission_date',
            field=models.DateField(blank=True, null=True, verbose_name='تاریخ مجوز قرارداد'),
        ),
    ]
