# Generated by Django 4.2 on 2023-05-17 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askme', '0014_alter_profile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='avatars/default-avatar.jpg', upload_to='avatars/%Y/%m/%d'),
        ),
    ]
