# Generated by Django 2.2.5 on 2020-01-18 12:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blog',
            old_name='last_update_time',
            new_name='last_updated_time',
        ),
    ]
