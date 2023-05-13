from django.contrib import auth
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.db.models import Count, Case, When, F
from django.urls import reverse
from askme.forms import LoginForm
from askme import models

# Create your views here.

# Converts num into human readable format (1000 -> 1K)


def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'),
                         ['', 'K', 'M', 'B', 'T'][magnitude])


def index(request):
    action = request.GET.get("action", None)
    if action == "log_out":
        models.USER["status"] = False
    elif action == "log_in":
        models.USER["status"] = True

    questions = models.Question.objects
    questions = questions.get_newest()
    # questions = questions.count_answers()
    # questions = questions.count_rating()

    popular_tags = models.Tag.objects.get_top_tags(10)

    try:
        page = paginate(questions, request, per_page=5)
    except ValueError:
        return HttpResponseBadRequest("Bad request")

    context = {
        'questions': page,
        'user': models.USER,
        'popular_tags': popular_tags,
    }
    return render(request, 'index.html', context)


def question(request, question_id):
    question = models.Question.objects.get(id=question_id)
    # question.rating = question.count_rating()
    answers = question.answer_set.all()
    # answers = answers.count_rating()
    answers = answers.get_hottest()

    popular_tags = models.Tag.objects.get_top_tags(10)

    try:
        page = paginate(answers, request, per_page=3)
    except ValueError:
        return HttpResponseBadRequest("Bad request")

    context = {
        "question": question,
        "answers": page,
        "user": models.USER,
        'popular_tags': popular_tags,
    }
    return render(request, 'question-page.html', context)


def ask(request):
    popular_tags = models.Tag.objects.get_top_tags(10)

    context = {
        "user": models.USER,
        'popular_tags': popular_tags,
    }
    return render(request, 'ask.html', context)


def settings(request):
    popular_tags = models.Tag.objects.get_top_tags(10)

    context = {
        "user": models.USER,
        'popular_tags': popular_tags,
    }
    return render(request, 'settings.html', context)


def hot(request):
    questions = models.Question.objects
    # questions = questions.count_answers()
    # questions = questions.count_rating()
    questions = questions.get_hottest()

    popular_tags = models.Tag.objects.get_top_tags(10)

    try:
        page = paginate(questions, request, per_page=5)
    except ValueError:
        return HttpResponseBadRequest("Bad request")

    context = {
        'questions': page,
        'user': models.USER,
        'popular_tags': popular_tags,
    }
    return render(request, 'hot-questions.html', context)


def tag(request, tag_name):
    questions = models.Question.objects.get_tag_questions(tag_name)
    questions = questions.get_newest()

    popular_tags = models.Tag.objects.get_top_tags(10)

    try:
        page = paginate(questions, request, per_page=5)
    except ValueError:
        return HttpResponseBadRequest("Bad request")

    context = {
        'questions': page,
        'tag_name': tag_name,
        'user': models.USER,
        'popular_tags': popular_tags,
    }
    return render(request, 'tag-questions.html', context)


def log_in(request):
    popular_tags = models.Tag.objects.get_top_tags(10)

    if request.method == "GET":
        login_form = LoginForm()
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            print(login_form.cleaned_data)
            user = auth.authenticate(request=request, **login_form.cleaned_data)
            if user:
                login(request, user)
                return redirect(reverse('index'))

            login_form.add_error(None, "Invalid username or password")


    context = {
        'user': models.USER,
        'popular_tags': popular_tags,
        'form': login_form,
    }
    return render(request, 'log-in.html', context)


def signin(request):
    popular_tags = models.Tag.objects.get_top_tags(10)

    context = {
        'user': models.USER,
        'popular_tags': popular_tags,
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
