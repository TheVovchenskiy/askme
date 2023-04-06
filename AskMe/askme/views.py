from django.shortcuts import render
from . import models

# Create your views here.


def index(request):
    action = request.GET.get("action", None)

    if action == "log_out":
        models.USER["status"] = False
    elif action == "log_in":
        models.USER["status"] = True
    
    context = {
        'questions': models.QUESTIONS,
        'user': models.USER,
    }
    return render(request, 'index.html', context)


def question(request, questionID):
    if questionID > len(models.QUESTIONS) - 1:
        questionID = len(models.QUESTIONS) - 1
    
    context = {
        "question": models.QUESTIONS[questionID],
        "answers": models.ANSWERS,
        "user": models.USER,
    }
    return render(request, 'question.html', context)


def ask(request):
    context = {
        "user": models.USER,
    }
    return render(request, 'ask.html', context)


def settings(request):
    context = {
        "user": models.USER,
    }
    return render(request, 'settings.html', context)


def hot(request):
    context = {
        'questions': models.QUESTIONS,
        "user": models.USER,
    }
    return render(request, 'hot-questions.html', context)