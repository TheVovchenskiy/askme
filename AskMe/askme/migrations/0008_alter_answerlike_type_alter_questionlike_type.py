# Generated by Django 4.2 on 2023-04-12 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askme', '0007_remove_profile_rating_alter_question_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answerlike',
            name='type',
            field=models.CharField(choices=[('like', 'Like'), ('dislike', 'Dislike')], max_length=7),
        ),
        migrations.AlterField(
            model_name='questionlike',
            name='type',
            field=models.CharField(choices=[('like', 'Like'), ('dislike', 'Dislike')], max_length=7),
        ),
    ]
