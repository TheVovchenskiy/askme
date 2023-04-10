from django.db import models
from django.contrib.auth.models import User

QUESTIONS = [
    {
        'id': i,
        'title': f'Question {i}',
        'text': f'Text {i}',
    } for i in range(100)
]

ANSWERS = [
    {
        'id': i,
        'text': f'Text {i}',
        'correct': i / 5 < 0.5,
    } for i in range(5)
]

USER = {
    'status': True,
}

POPULAR_TAGS = [
    {
        'tag_name': f'tag_{i}',
    } for i in range(15)
]

QUESTION_TAGS = [
    {
        'tag_name': f'tag_{i}',
    } for i in range(4)
]


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField()
    author = models.ForeignKey(
        'Profile',
        on_delete=models.PROTECT
    )
    tag = models.ManyToManyField('Tag')


class QuestionLikes(models.Model):
    question = models.ForeignKey(
        'Question',
        on_delete=models.PROTECT
    )
    value = models.IntegerField()


class Answer(models.Model):
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    correct_flag = models.BooleanField()
    rating = models.IntegerField()
    question = models.ForeignKey(
        'Question',
        on_delete=models.PROTECT
    )
    author = models.ForeignKey(
        'Profile',
        on_delete=models.PROTECT
    )


class AnswerLike(models.Model):
    answer = models.ForeignKey(
        'Answer',
        on_delete=models.PROTECT
    )
    value = models.IntegerField()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # avatar
    signup_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField()


class Tag(models.Model):
    tag_name = models.CharField(max_length=30)
