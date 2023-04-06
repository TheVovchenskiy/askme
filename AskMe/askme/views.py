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
        'popular_tags': models.POPULAR_TAGS,
        'question_tags': models.QUESTION_TAGS,
    }
    return render(request, 'index.html', context)


def question(request, question_id):
    question_id = min(len(models.QUESTIONS) - 1, question_id)
    
    context = {
        "question": models.QUESTIONS[question_id],
        "answers": models.ANSWERS,
        "user": models.USER,
        'popular_tags': models.POPULAR_TAGS,
        'question_tags': models.QUESTION_TAGS,
    }
    return render(request, 'question-page.html', context)


def ask(request):
    context = {
        "user": models.USER,
        'popular_tags': models.POPULAR_TAGS,
    }
    return render(request, 'ask.html', context)


def settings(request):
    context = {
        "user": models.USER,
        'popular_tags': models.POPULAR_TAGS,
    }
    return render(request, 'settings.html', context)


def hot(request):
    context = {
        'questions': models.QUESTIONS,
        'user': models.USER,
        'popular_tags': models.POPULAR_TAGS,
        'question_tags': models.QUESTION_TAGS,
    }
    return render(request, 'hot-questions.html', context)


def tag(request, tag_name):
    context = {
        'questions': models.QUESTIONS,
        'tag_name': tag_name,
        'user': models.USER,
        'popular_tags': models.POPULAR_TAGS,
        'question_tags': models.QUESTION_TAGS,
    }
    return render(request, 'tag-questions.html', context)