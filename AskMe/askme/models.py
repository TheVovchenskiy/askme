from django.db import models
from django.contrib.auth.models import User


USER = {
    "status": True
}

class QuestionManager(models.Manager):
    def get_newest(self):
        return self.order_by('-creation_date')
    
    def get_hottest(self):
        return self.order_by('-rating')


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField()
    author = models.ForeignKey(
        'Profile',
        on_delete=models.PROTECT
    )
    tag = models.ManyToManyField('Tag', blank=True)

    objects = QuestionManager()

    def __str__(self) -> str:
        return f"'{self.author.user.username}': {self.title}"


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

    def __str__(self) -> str:
        return f"Answer by '{self.author.user.username}' to {self.question}"


class AnswerLike(models.Model):
    answer = models.ForeignKey(
        'Answer',
        on_delete=models.PROTECT
    )
    value = models.IntegerField()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/%Y/%m/%d", blank=True)
    signup_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField()

    def __str__(self) -> str:
        return self.user.username


class Tag(models.Model):
    tag_name = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return self.tag_name
