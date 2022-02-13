# Generated by Django 2.2 on 2021-07-24 11:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0042_auto_20210621_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='vcc_free',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='xxx', to='contract.FreeVCC', verbose_name='کارت مجازی خالی'),
        ),
    ]
