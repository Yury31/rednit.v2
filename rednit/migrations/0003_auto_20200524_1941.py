# Generated by Django 3.0.6 on 2020-05-24 19:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rednit', '0002_chat_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='author',
        ),
        migrations.RemoveField(
            model_name='message',
            name='chat',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='user',
        ),
        migrations.DeleteModel(
            name='Chat',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
