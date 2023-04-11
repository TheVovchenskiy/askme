from django.db import models
from django.contrib.auth.models import User


USER = {
    "status": True
}


class QuestionLike(models.Model):
    user = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE
    )

    TYPE_CHOICES = [
        ('l', 'Like'),
        ('d', 'Dislike')
    ]
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self) -> str:
        return f"'{self.type}' by {self.user} to {self.question}"


class QuestionQuerySet(models.query.QuerySet):
    def get_newest(self):
        return self.order_by('-creation_date')

    def get_hottest(self):
        return self.order_by('-rating')

    def count_answers(self):
        return self.annotate(answers_count=models.Count('answer'))

    def count_rating(self):
        return self.annotate(
            likes=models.Count(models.Case(
                models.When(questionlike__type='l', then=1))),
            dislikes=models.Count(models.Case(
                models.When(questionlike__type='d', then=1))),
            rating=models.F('likes') - models.F('dislikes')
        )


class QuestionManager(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def get_newest(self):
        return self.get_queryset().get_newest()

    def get_hottest(self):
        return self.get_queryset().get_hottest()

    def count_answers(self):
        return self.get_queryset().count_answers()

    def count_rating(self):
        return self.get_queryset().count_rating


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    human_format_rating = models.CharField(
        max_length=15, null=True, blank=True)
    author = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE
    )
    tag = models.ManyToManyField('Tag', blank=True)

    objects = QuestionManager()

    def __str__(self) -> str:
        return f"'{self.author.user.username}': {self.title}"


class AnswerLike(models.Model):
    user = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE
    )
    answer = models.ForeignKey(
        'Answer',
        on_delete=models.CASCADE
    )

    TYPE_CHOICES = [
        ('l', 'Like'),
        ('d', 'Dislike')
    ]
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'answer')

    def __str__(self) -> str:
        return f"'{self.type}' by {self.user} to answer/{self.id}"


class AnswerQuerySet(models.query.QuerySet):
    def answers_by_questoin_id(self, question_id):
        return self.filter(question__id=question_id)

    def get_newest(self):
        return self.order_by('-creation_date')

    def get_hottest(self):
        return self.order_by('-rating')

    def count_rating(self):
        return self.annotate(
            likes=models.Count(models.Case(
                models.When(answerlike__type='l', then=1))),
            dislikes=models.Count(models.Case(
                models.When(answerlike__type='d', then=1))),
            rating=models.F('likes') - models.F('dislikes')
        )


class AnswerManager(models.Manager):
    def get_queryset(self):
        return AnswerQuerySet(self.model, using=self._db)

    def answers_by_questoin_id(self, question_id):
        return self.get_queryset().answers_by_questoin_id(question_id)

    def get_newest(self):
        return self.get_queryset().get_newest()

    def count_answers(self):
        return self.get_queryset().count_answers()

    def count_rating(self):
        return self.get_queryset().count_rating


class Answer(models.Model):
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    correct_flag = models.BooleanField()
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE
    )

    objects = AnswerManager()

    def __str__(self) -> str:
        return f"Answer by '{self.author}' to {self.question}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/%Y/%m/%d", blank=True)
    signup_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField()

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url

    def __str__(self) -> str:
        return self.user.username


class Tag(models.Model):
    tag_name = models.CharField(max_length=30, unique=True)

    def __str__(self) -> str:
        return self.tag_name
