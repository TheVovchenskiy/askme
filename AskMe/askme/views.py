from django.contrib import auth
# from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.db.models import Count, Case, When, F
from django.urls import reverse
from askme.forms import AddAnswerForm, AddQuestionForm, LoginForm, RegistrationForm, SettingsForm
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
    answers = question.answer_set.all()
    answers = answers.get_hottest()

    popular_tags = models.Tag.objects.get_top_tags(10)

    try:
        page = paginate(answers, request, per_page=3)
    except ValueError:
        return HttpResponseBadRequest("Bad request")

    if request.method == "GET":
        add_answer_form = AddAnswerForm()
    elif request.method == "POST":
        add_answer_form = AddAnswerForm(request.POST)
        if add_answer_form.is_valid():
            content = add_answer_form.cleaned_data['content']

            answer = models.Answer(
                content=content,
                question=question,
                author=models.Profile.objects.get(user=curr_user)
            )
            answer.save()

            if models.Answer.objects.filter(id=answer.id):
                return redirect(
                    'question',
                    question_id=question.id,
                )
            else:
                add_answer_form.add_error(
                    field=None, error='Answer adding error')

    context = {
        'question': question,
        'answers': page,
        'user': curr_user,
        'user_avatar': user_avatar,
        'popular_tags': popular_tags,
        'form': add_answer_form,
    }
    return render(request, 'question-page.html', context)


@login_required(login_url='login', redirect_field_name='continue')
@require_http_methods(['GET', 'POST'])
def ask(request):
    curr_user = checkUserAuth(request)
    user_avatar = getUserAvatar(curr_user)
    popular_tags = models.Tag.objects.get_top_tags(10)

    print(request.GET)
    print(request.POST)

    if request.method == "GET":
        add_question_form = AddQuestionForm()
    elif request.method == "POST":
        add_question_form = AddQuestionForm(request.POST)
        if add_question_form.is_valid():
            title = add_question_form.cleaned_data['title']
            content = add_question_form.cleaned_data['content']
            tags = add_question_form.cleaned_data['tags']
            tags = getTagsList(tags)
            addAbsentTags(tags)

            question = models.Question(
                title=title,
                content=content,
                author=models.Profile.objects.get(user=curr_user)
            )

            selected_tags = [models.Tag.objects.get(tag_name=tag_name)
                             for tag_name in tags]
            print(selected_tags)

            question.save()
            question.tag.add(*selected_tags)

            if models.Question.objects.filter(id=question.id):
                return redirect('question', question_id=question.id)
            else:
                add_question_form.add_error(
                    field=None, error='Question adding error')

    context = {
        'user': curr_user,
        'user_avatar': user_avatar,
        'popular_tags': popular_tags,
        'form': add_question_form,
    }
    return render(request, 'ask.html', context)


def getTagsList(tags):
    return tags.split()


def addAbsentTags(tags):
    for tag in tags:
        if not models.Tag.objects.filter(tag_name=tag):
            models.Tag(tag_name=tag).save()


@login_required(login_url='login', redirect_field_name='continue')
@require_http_methods(['GET', 'POST'])
def settings(request):
    curr_user = checkUserAuth(request)
    user_avatar = getUserAvatar(curr_user)
    popular_tags = models.Tag.objects.get_top_tags(10)

    if request.method == "GET":
        settings_form = SettingsForm(initial={
            'username': curr_user.username,
            'email': curr_user.email,
            'avatar': None
        })
    elif request.method == "POST":
        settings_form = SettingsForm(
            request.POST,
            files=request.FILES,
            instance=curr_user
        )
        if settings_form.is_valid():
            settings_form.save()
            if curr_user:
                return redirect('settings')
            else:
                settings_form.add_error(field=None, error='User saving error')

    context = {
        'user': curr_user,
        'user_avatar': user_avatar,
        'popular_tags': popular_tags,
        'form': settings_form,
    }
    return render(request, 'settings.html', context)


def hot(request):
    curr_user = checkUserAuth(request)
    user_avatar = getUserAvatar(curr_user)

    questions = models.Question.objects
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
        user_form = RegistrationForm(
            request.POST,
            files=request.FILES,
        )
        if user_form.is_valid():
            new_user = user_form.save()
            if new_user:
                auth.login(request, new_user)
                # new_profile = models.Profile(user=new_user)
                # new_profile.save()
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


@login_required
@require_POST
def vote_up(request):
    question_id = request.POST['question_id']
    question = models.Question.objects.get(id=question_id)

    votes = question.questionlike_set.filter(user=request.user.profile)

    if not votes:
        like = models.QuestionLike(
            user=request.user.profile,
            question=question,
            type=models.LIKE,
        )
        like.save()
        question.rating += 1
        question.save()

    elif votes[0].type == models.DISLIKE:
        votes[0].type = models.LIKE
        votes[0].save()

        question.rating += 2
        question.save()

    else:
        votes[0].delete()

        question.rating -= 1
        question.save()

    return JsonResponse({
        'new_rating': question.rating,
    })


@login_required
@require_POST
def vote_down(request):
    question_id = request.POST['question_id']
    question = models.Question.objects.get(id=question_id)

    votes = question.questionlike_set.filter(user=request.user.profile)

    if not votes:
        dislike = models.QuestionLike(
            user=request.user.profile,
            question=question,
            type=models.DISLIKE,
        )
        dislike.save()
        question.rating -= 1
        question.save()

    elif votes[0].type == models.LIKE:
        votes[0].type = models.DISLIKE
        votes[0].save()

        question.rating -= 2
        question.save()

    else:
        votes[0].delete()

        question.rating += 1
        question.save()

    return JsonResponse({
        'new_rating': question.rating,
    })
