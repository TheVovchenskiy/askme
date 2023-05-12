from django.urls import path
from askme import views

urlpatterns = [
    path('', views.index, name="index"),
    path('question/<int:question_id>', views.question, name="question"),
    path('ask', views.ask, name='ask'),
    path('settings', views.settings, name='settings'),
    path('hot', views.hot, name='hot'),
    path('tag/<str:tag_name>', views.tag, name='tag'),
    path('login', views.login, name='login'),
    path('signin', views.signin, name='signin'),
]
