from django.contrib import admin
from askme.models import Question, QuestionLikes, Answer, AnswerLike, Profile, Tag


admin.site.register(Question)
admin.site.register(QuestionLikes)
admin.site.register(Answer)
admin.site.register(AnswerLike)
admin.site.register(Profile)
admin.site.register(Tag)
