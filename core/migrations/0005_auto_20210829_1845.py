# Generated by Django 3.2.5 on 2021-08-29 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_driver'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='age',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='groupmembership',
            name='reg_no',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
