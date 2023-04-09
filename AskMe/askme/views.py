from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.core.paginator import Paginator
from . import models

# Create your views here.


def index(request):
    action = request.GET.get("action", None)

    if action == "log_out":
        models.USER["status"] = False
    elif action == "log_in":
        models.USER["status"] = True

    try:
        page = paginate(models.QUESTIONS, request, per_page=5)
    except ValueError:
        return HttpResponseBadRequest("Bad request")

    context = {
        'questions': page,
        'user': models.USER,
        'popular_tags': models.POPULAR_TAGS,
        'question_tags': models.QUESTION_TAGS,
    }
    return render(request, 'index.html', context)


def question(request, question_id):
    question_id = min(len(models.QUESTIONS) - 1, question_id)

    try:
        page = paginate(models.ANSWERS, request, per_page=3)
    except ValueError:
        return HttpResponseBadRequest("Bad request")

    context = {
        "question": models.QUESTIONS[question_id],
        "answers": page,
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
    try:
        page = paginate(models.QUESTIONS, request, per_page=5)
    except ValueError:
        return HttpResponseBadRequest("Bad request")
    context = {
        'questions': page,
        'user': models.USER,
        'popular_tags': models.POPULAR_TAGS,
        'question_tags': models.QUESTION_TAGS,
    }
    return render(request, 'hot-questions.html', context)


def tag(request, tag_name):
    try:
        page = paginate(models.QUESTIONS, request, per_page=5)
    except ValueError:
        return HttpResponseBadRequest("Bad request")

    context = {
        'questions': page,
        'tag_name': tag_name,
        'user': models.USER,
        'popular_tags': models.POPULAR_TAGS,
        'question_tags': models.QUESTION_TAGS,
    }
    return render(request, 'tag-questions.html', context)


def login(request):
    context = {
        'user': models.USER,
        'popular_tags': models.POPULAR_TAGS,
    }
    return render(request, 'log-in.html', context)


def signin(request):
    context = {
        'user': models.USER,
        'popular_tags': models.POPULAR_TAGS,
    }
    return render(request, 'sign-in.html', context)


def paginate(objects_list, request, per_page=10):
    DEFAULT_PAGE_NUM = 1

    paginator = Paginator(objects_list, per_page)

    page_num = request.GET.get('page', DEFAULT_PAGE_NUM)

    try:
        page_num = int(page_num)
    except ValueError:
        raise ValueError

    if page_num < 1:
        page_num = DEFAULT_PAGE_NUM
    elif page_num > paginator.num_pages:
        page_num = paginator.num_pages

    page = paginator.get_page(page_num)
    page.adjusted_elided_pages = paginator.get_elided_page_range(
        page_num, on_each_side=1, on_ends=1)

    return page
