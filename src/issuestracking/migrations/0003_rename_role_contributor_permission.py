# Generated by Django 3.2 on 2022-02-21 15:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issuestracking', '0002_alter_contributor_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contributor',
            old_name='role',
            new_name='permission',
        ),
    ]
