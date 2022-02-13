# Generated by Django 2.2 on 2021-09-01 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0048_auto_20210823_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractsuretys',
            name='order',
            field=models.CharField(choices=[('1', 'ضامن اول'), ('2', 'ضامن دوم')], default='1', max_length=1, verbose_name='ترتیب ضامن'),
        ),
        migrations.AlterField(
            model_name='contractsuretys',
            name='surt',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='customer.customer', verbose_name='ضامن'),
            preserve_default=False,
        ),
    ]
