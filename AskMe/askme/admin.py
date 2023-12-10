from django.contrib import admin
from askme.models import QuestionLike, Question, Answer, AnswerLike, Profile, Tag


admin.site.register(Question)
admin.site.register(QuestionLike)
admin.site.register(Answer)
admin.site.register(AnswerLike)
admin.site.register(Profile)
admin.site.register(Tag)
