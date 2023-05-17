from django.contrib import auth
# from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.db.models import Count, Case, When, F
from django.urls import reverse
from askme.forms import LoginForm, RegistrationForm
from askme import models

# Create your views here.

# Converts num into human readable format (1000 -> 1K)


def humanFormat(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'),
                         ['', 'K', 'M', 'B', 'T'][magnitude])


def index(request):
    curr_user = checkUserAuth(request)
    user_avatar = getUserAvatar(curr_user)

    # print(curr_user)
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
        'user': curr_user,
        'user_avatar': user_avatar,
        'popular_tags': popular_tags,
    }
    return render(request, 'index.html', context)


def question(request, question_id):
    curr_user = checkUserAuth(request)
    user_avatar = getUserAvatar(curr_user)

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
        'question': question,
        'answers': page,
        'user': curr_user,
        'user_avatar': user_avatar,
        'popular_tags': popular_tags,
    }
    return render(request, 'question-page.html', context)


@login_required(login_url='login', redirect_field_name='continue')
def ask(request):
    curr_user = checkUserAuth(request)
    user_avatar = getUserAvatar(curr_user)

    popular_tags = models.Tag.objects.get_top_tags(10)

    context = {
        'user': curr_user,
        'user_avatar': user_avatar,
        'popular_tags': popular_tags,
    }
    return render(request, 'ask.html', context)


@login_required(login_url='login', redirect_field_name='continue')
def settings(request):
    curr_user = checkUserAuth(request)
    user_avatar = getUserAvatar(curr_user)
    popular_tags = models.Tag.objects.get_top_tags(10)

    context = {
        'user': curr_user,
        'user_avatar': user_avatar,
        'popular_tags': popular_tags,
    }
    return render(request, 'settings.html', context)


def hot(request):
    curr_user = checkUserAuth(request)
    user_avatar = getUserAvatar(curr_user)

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
        'user': curr_user,
        'user_avatar': user_avatar,
        'popular_tags': popular_tags,
    }
    return render(request, 'hot-questions.html', context)


def tag(request, tag_name):
    curr_user = checkUserAuth(request)
    user_avatar = getUserAvatar(curr_user)

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
        'user': curr_user,
        'user_avatar': user_avatar,
        'popular_tags': popular_tags,
    }
    return render(request, 'tag-questions.html', context)


def login(request):
    curr_user = checkUserAuth(request)
    if curr_user:
        return redirect(reverse('index'))

    # print("HTTP_REFERER: ", request.META.get('HTTP_REFERER'))
    
    popular_tags = models.Tag.objects.get_top_tags(10)

    if request.method == "GET":
        login_form = LoginForm()
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            # print(login_form.cleaned_data)
            user = auth.authenticate(
                request=request, **login_form.cleaned_data)
            if user:
                auth.login(request, user)
                continue_url = request.GET.get('continue', reverse('index'))
                print(continue_url)
                return redirect(continue_url)

            login_form.add_error(None, "Invalid username or password")

    context = {
        'user': curr_user,
        'popular_tags': popular_tags,
        'form': login_form,
    }
    return render(request, 'log-in.html', context)


def logout(request):
    auth.logout(request)
    continue_url = request.GET.get('continue', reverse('index'))
    return redirect(continue_url)


def signup(request):
    curr_user = checkUserAuth(request)
    if curr_user:
        return redirect(reverse('index'))

    popular_tags = models.Tag.objects.get_top_tags(10)

    if request.method == "GET":
        user_form = RegistrationForm()
    elif request.method == "POST":
        user_form = RegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save()
            if new_user:
                auth.login(request, new_user)
                new_profile = models.Profile(user=new_user)
                new_profile.save()
                return redirect(reverse('index'))
            else:
                user_form.add_error(field=None, error='User saving error')

    context = {
        'user': curr_user,
        'popular_tags': popular_tags,
        'form': user_form,
    }
    return render(request, 'sign-up.html', context)


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


def checkUserAuth(request):
    curr_user = request.user
    if curr_user.is_anonymous:
        curr_user = None

    return curr_user


def getUserAvatar(user):
    if user:
        profile = models.Profile.objects.get(user=user)
        avatar = profile.avatar
    else:
        avatar = None
    return avatar