# Generated by Django 4.1.6 on 2023-02-23 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0014_remove_score_score_score_servant_partner'),
    ]

    operations = [
        migrations.AddField(
            model_name='statue',
            name='scored_count',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]