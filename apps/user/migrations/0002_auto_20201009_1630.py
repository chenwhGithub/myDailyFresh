# Generated by Django 3.1.1 on 2020-10-09 08:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='created_time',
        ),
        migrations.RemoveField(
            model_name='address',
            name='is_deleted',
        ),
        migrations.RemoveField(
            model_name='address',
            name='updated_time',
        ),
        migrations.RemoveField(
            model_name='user',
            name='created_time',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_deleted',
        ),
        migrations.RemoveField(
            model_name='user',
            name='updated_time',
        ),
    ]