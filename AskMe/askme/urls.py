from django.urls import path
from django.contrib.auth import views as authViews
from askme import views

urlpatterns = [
    path('', views.index, name="index"),
    path('question/<int:question_id>', views.question, name="question"),
    path('ask', views.ask, name='ask'),
    path('settings', views.settings, name='settings'),
    path('hot', views.hot, name='hot'),
    path('tag/<str:tag_name>', views.tag, name='tag'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('signup', views.signup, name='signup'),
    path('vote_up', views.vote_up, name='vote_up'),
    path('vote_down', views.vote_down, name='vote_down'),
]
