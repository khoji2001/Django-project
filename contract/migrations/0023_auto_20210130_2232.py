# Generated by Django 2.2 on 2021-01-30 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0022_contractsuretys'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractsuretys',
            name='order',
            field=models.CharField(choices=[('1', 'ضامن اول'), ('2', 'ضامن دوم')], max_length=1, verbose_name='ترتیب ضامن'),
        ),
    ]