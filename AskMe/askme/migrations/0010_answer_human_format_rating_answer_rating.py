# Generated by Django 4.2 on 2023-05-12 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('askme', '0009_question_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='human_format_rating',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='answer',
            name='rating',
            field=models.IntegerField(default=0),
        ),
    ]
