#in the name of allah
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0010_auto_20201109_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='job_class',
            field=models.CharField(choices=[('0', 'کارمند'), ('1', 'آزاد'), ('2', 'مستمری بگیر')], default='0', max_length=1, verbose_name='حوزه شغلی'),
        ),
        migrations.AlterField(
            model_name='surety',
            name='job_class',
            field=models.CharField(choices=[('0', 'کارمند'), ('1', 'آزاد'), ('2', 'مستمری بگیر')], default='0', max_length=1, verbose_name='حوزه شغلی'),
        ),
    ]
