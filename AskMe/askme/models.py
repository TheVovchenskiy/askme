from django.db import models
from django.contrib.auth.models import User


LIKE = 'like'
DISLIKE = 'dislike'


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
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike')
    ]
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
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

    # def count_answers(self):
    #     return self.annotate(answers_count=models.Count('answer'))

    def get_tag_questions(self, tag_name):
        return self.filter(tag__tag_name=tag_name)


class QuestionManager(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def get_newest(self):
        return self.get_queryset().get_newest()

    def get_hottest(self):
        return self.get_queryset().get_hottest()

    # def count_answers(self):
    #     return self.get_queryset().count_answers()

    def get_tag_questions(self, tag_name):
        return self.get_queryset().get_tag_questions(tag_name)


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    human_format_rating = models.CharField(
        max_length=15, null=True, blank=True)
    author = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE
    )
    tag = models.ManyToManyField('Tag', blank=True)

    objects = QuestionManager()

    def setRating(self):
        likes = QuestionLike.objects.filter(question=self, type='like').count()
        dislikes = QuestionLike.objects.filter(
            question=self, type='dislike').count()
        self.rating = likes - dislikes

    def answers_count(self):
        return Answer.objects.filter(question=self).count()

    def __str__(self) -> str:
        return f"Question #{self.id}"


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
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike')
    ]
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
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


class AnswerManager(models.Manager):
    def get_queryset(self):
        return AnswerQuerySet(self.model, using=self._db)

    def answers_by_questoin_id(self, question_id):
        return self.get_queryset().answers_by_questoin_id(question_id)

    def get_newest(self):
        return self.get_queryset().get_newest()

    def count_answers(self):
        return self.get_queryset().count_answers()


class Answer(models.Model):
    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    correct_flag = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)
    # human_format_rating = models.CharField(
    #     max_length=15, null=True, blank=True)
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        'Profile',
        on_delete=models.CASCADE
    )

    objects = AnswerManager()

    def setRating(self):
        likes = AnswerLike.objects.filter(answer=self, type='like').count()
        dislikes = AnswerLike.objects.filter(
            answer=self, type='dislike').count()
        self.rating = likes - dislikes

    def __str__(self) -> str:
        return f"Answer by '{self.author}' to {self.question}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to="avatars/%Y/%m/%d",
        default='avatars/default_avatar.jpg'
    )
    signup_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.user.username


class TagManager(models.Manager):
    def get_top_tags(self, top_count):
        return self.annotate(total_count=models.Count('question')).order_by('-total_count')[:top_count]


class Tag(models.Model):
    tag_name = models.CharField(max_length=30, unique=True)

    objects = TagManager()

    def __str__(self) -> str:
        return self.tag_name
