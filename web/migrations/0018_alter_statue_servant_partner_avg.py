# Generated by Django 4.1.6 on 2023-03-04 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0017_remove_statue_servant_partner_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statue',
            name='servant_partner_avg',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=5),
        ),
    ]