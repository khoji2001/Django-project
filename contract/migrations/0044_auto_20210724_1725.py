# Generated by Django 2.2 on 2021-07-24 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0043_contract_vcc_free'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='vcc_free',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='null_contract', to='contract.FreeVCC', verbose_name='کارت مجازی خالی'),
        ),
    ]
