# Generated by Django 3.2.3 on 2022-01-19 18:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0008_auto_20210901_2014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupmembership',
            name='members',
        ),
        migrations.DeleteModel(
            name='IndividualMembership',
        ),
        migrations.RemoveField(
            model_name='loader',
            name='vehicle',
        ),
        migrations.RemoveField(
            model_name='offence',
            name='driver',
        ),
        migrations.RemoveField(
            model_name='offence',
            name='vehicle_involved',
        ),
        migrations.RemoveField(
            model_name='driver',
            name='age',
        ),
        migrations.RemoveField(
            model_name='driver',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='driver',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='driver',
            name='phone_no',
        ),
        migrations.AddField(
            model_name='driver',
            name='license_no',
            field=models.CharField(default=1, max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='driver',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='accounts.customuser'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='driver',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.vehicle'),
        ),
        migrations.DeleteModel(
            name='GroupMembership',
        ),
        migrations.DeleteModel(
            name='Loader',
        ),
        migrations.DeleteModel(
            name='Offence',
        ),
        migrations.DeleteModel(
            name='SmallScaleMembers',
        ),
    ]
