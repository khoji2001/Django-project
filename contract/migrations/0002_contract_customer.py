# Generated by Django 2.2 on 2020-06-08 18:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
        ('contract', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer.customer', verbose_name='متقاضی'),
        ),
    ]
