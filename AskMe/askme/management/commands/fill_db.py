from askme import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from lorem.text import TextLorem
from random_username.generate import generate_username
import random
import string
import sys


class Command(BaseCommand):
    help = 'Fills the Data Base with data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Number of profiles')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        # fill_data_base(ratio)
        print(ratio)


def generate_password(length):
    # Создаем список символов, которые могут быть в пароле
    characters = string.ascii_letters + string.digits + string.punctuation
    # Генерируем пароль случайной длины
    password = ''.join(random.choice(characters) for i in range(length))
    return password


def generate_email(username):
    letters = string.ascii_lowercase
    domain = ''.join(random.choice(letters) for i in range(5))
    extension = random.choice(['com', 'net', 'org'])
    return f"{username}@{domain}.{extension}"


def generate_user(passw_len_from=8, passw_len_to=16):
    username = generate_username()
    email = generate_email(username)
    password = generate_password(random.randint(passw_len_from, passw_len_to))

    return User.objects.create_user(
        username=username,
        email=email,
        password=password
    )


def generate_profile(av_id_from=1, av_id_to=10):
    user = generate_user()
    profile = models.Profile(user=user)
    avatar_id = random.randint(av_id_from, av_id_to)
    with open(f'avatars/avatar-{avatar_id}', 'rb') as image:
        image_data = image.read()

    profile.avatar.save(f'avatar-{user.useraname}', ContentFile(image_data))
    return profile


def generate_question_title(wrds_count_from=4, wrds_count_to=8):
    return TextLorem(srange=(wrds_count_from, wrds_count_to)).sentence()


def generate_question_content(
        sntc_len_from=5, sntc_len_to=10,
        par_len_from=7, par_len_to=15,
        txt_len_from=1, txt_len_to=3):
    return TextLorem(srange=(
        sntc_len_from, sntc_len_to),
        prange=(par_len_from, par_len_to),
        trange=(txt_len_from, txt_len_to)
    ).text()


def get_random_instances(objects, objects_count=1):
    return objects.order_by('?')[:objects_count]


def generate_question():
    return models.Question(
        title=generate_question_title(),
        content=generate_question_content(),
        author=get_random_instances(models.Profile.objects),
    )


def generate_answer_content(srange=(5, 10), prange=(5, 10), trange=(1, 3)):
    return TextLorem(srange=srange, prange=prange, trange=trange)


def generate_answer_correct_flag(true_weight=0.2, false_weight=0.8):
    correct_flags = [True, False]
    correct_flags_weights = [true_weight, false_weight]
    return random.choices(correct_flags, correct_flags_weights)[0]


def generate_answer():
    return models.Answer(
        content=generate_answer_content(),
        correct_flag=generate_answer_correct_flag(),
        question=get_random_instances(models.Question.objects),
        author=get_random_instances(models.Profile.objects),
    )


def generate_tag_name(length_from=3, length_to=7):
    letters = string.ascii_lowercase
    range_value = random.randint(length_from, length_to)
    return ''.join(random.choice(letters) for i in range(range_value))


def generate_tag():
    return models.Tag(
        tag_name=generate_tag_name(length_from=3, length_to=7),
    )


def get_random_vote(like_weight, dislike_wieight):
    vote_type_choices = ['like', 'dislike']
    vote_type_weights = [like_weight, dislike_wieight]
    return random.choices(vote_type_choices, vote_type_weights)[0]


def generate_question_like(like_weight=0.5, dislike_wieight=0.5):
    user = get_random_instances(models.Profile.objects).get()
    question = get_random_instances(models.Question.objects).get()
    type = get_random_vote(like_weight, dislike_wieight)

    while True:
        if not models.QuestionLike.objects.filter(
            user=user,
            question=question,
        ).exists():
            return models.QuestionLike(
                user=user,
                question=question,
                type=type
            )


def generate_answer_like(like_weight=0.4, dislike_wieight=0.3):
    user = get_random_instances(models.Profile.objects).get()
    answer = get_random_instances(models.Answer.objects).get()

    while True:
        if not models.AnswerLike.objects.filter(
            user=user,
            answer=answer,
        ).exists():
            if answer.correct_flag:
                type = get_random_vote(0.9, 0.1)
            else:
                type = get_random_vote(like_weight, dislike_wieight)

            return models.AnswerLike(
                user=user,
                answer=answer,
                type=type
            )


def create_profiles(prof_count, batch_size, av_count):
    prof_left = prof_count
    print('Profiles created:')
    while prof_left > 0:
        models.Profile.objects.bulk_create(
            [generate_profile(av_id_to=av_count - 1)
             for i in range(batch_size)]
        )
        prof_left = - batch_size
        print(f'\r{prof_count - prof_left}/{prof_count}', end='')
    print()


def create_questions(quest_count, batch_size):
    quest_left = quest_count
    print('Questions created:')
    while quest_left > 0:
        models.Question.objects.bulk_create(
            [generate_question() for i in range(batch_size)]
        )
        quest_left = - batch_size
        print(f'\r{quest_count - quest_left}/{quest_count}', end='')
    print()


def create_question_likes(likes_count, batch_size):
    likes_left = likes_count
    while likes_left > 0:
        models.QuestionLike.objects.bulk_create(
            [generate_question_like() for i in range(batch_size)]
        )
        likes_left -= batch_size
        print(f'\r{likes_count - likes_left}/{likes_count}', end='')
    print()


def create_answer_likes(likes_count, batch_size):
    likes_left = likes_count
    while likes_left > 0:
        models.AnswerLike.objects.bulk_create(
            [generate_answer_like() for i in range(batch_size)]
        )
        likes_left -= batch_size
        print(f'\r{likes_count - likes_left}/{likes_count}', end='')
    print()


def create_answers(answ_count, batch_size):
    answ_left = answ_count
    while answ_left > 0:
        models.Answer.objects.bulk_create(
            [generate_answer() for i in range(batch_size)]
        )
        answ_left = - batch_size
        print(f'\r{answ_count - answ_left}/{answ_count}', end='')
    print()


def create_tags(tag_count, batch_size):
    tag_left = tag_count
    while tag_left > 0:
        models.Tag.objects.bulk_create(
            [generate_tag() for i in range(batch_size)]
        )
        tag_left = - batch_size
        print(f'\r{tag_count - tag_left}/{tag_count}', end='')
    print()


def link_questions2tags(tags_per_question_max=6):
    for question in models.Question.objects.all():
        tags_per_question = random.randint(1, tags_per_question_max)
        question.tag.add(
            *get_random_instances(models.Tag.objects, tags_per_question)
        )


def fill_data_base(ratio):
    PROFILES_COUNT = ratio
    QUESTIONS_COUNT = ratio * 10
    ANSWERS_COUNT = ratio * 100
    TAGS_COUNT = ratio
    VOTES_COUNT = ratio * 200
    print(ratio)


if __name__ == '__main__':
    main()
