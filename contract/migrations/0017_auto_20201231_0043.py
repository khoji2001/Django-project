# Generated by Django 2.2 on 2020-12-30 21:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0016_auto_20201230_2243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='contract.contract', verbose_name='قرارداد'),
        ),
    ]
