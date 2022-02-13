# Generated by Django 2.2 on 2021-01-30 18:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0018_auto_20210118_1552'),
        ('contract', '0021_contract_face_net_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractSuretys',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب ضامن')),
                ('cont', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suretys', to='contract.contract', verbose_name='قرارداد')),
                ('surt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='customer.surety', verbose_name='ضامن')),
            ],
            options={
                'verbose_name': 'ضامن',
                'verbose_name_plural': 'ضامنین',
            },
        ),
    ]
