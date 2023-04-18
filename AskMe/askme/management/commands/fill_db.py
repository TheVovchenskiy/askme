from askme import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor
from faker import Faker
from faker.providers import internet, lorem
import random
import string
from tqdm import tqdm
import os


Faker.seed(0)
fake = Faker()

BATCH_SIZE = 10_000

class Command(BaseCommand):
    help = 'Fills the Data Base with data'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Number of profiles')

    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        fill_data_base(ratio)
        # print(__file__)


def generate_password(length):
    # Создаем список символов, которые могут быть в пароле
    characters = string.ascii_letters + string.digits + string.punctuation
    # Генерируем пароль случайной длины
    password = ''.join(random.choice(characters) for i in range(length))
    return password


def generate_email():
    return fake.ascii_safe_email()


def generate_user(passw_len_from=8, passw_len_to=16):
    username = fake.user_name()
    email = generate_email()
    password = generate_password(random.randint(passw_len_from, passw_len_to))

    return User(
        username=username,
        email=email,
        password=password
    )


def create_users(us_count):
    print('Creating users')

    usrs = []
    profiles = []

    emails = set()
    usrnames = set()

    with tqdm(total=us_count) as pbar:
        with transaction.atomic(), ThreadPoolExecutor() as executor:
            while len(usrs) < us_count:
                user = generate_user()
                if user.username not in usrnames and \
                        user.email not in emails:
                    profile = models.Profile(user=user)
                    usrs.append(user)
                    profiles.append(profile)
                    emails.add(user.email)
                    usrnames.add(user.username)
                    pbar.update(1)

    User.objects.bulk_create(usrs)
    models.Profile.objects.bulk_create(profiles)
    print('Users created successfully')
    print()


def get_random_avatar(av_id_from=1, av_id_to=10):
    avatar_id = random.randint(av_id_from, av_id_to)
    with open(f'avatars/avatar-{avatar_id}.jpg', 'rb') as image:
        image_data = image.read()

    return image_data


def link_avatars2profiles(av_count):
    print('Creating Profile avatars')

    profiles = models.Profile.objects.all()

    for profile in tqdm(profiles):
        image_data = get_random_avatar(av_id_to=av_count-1)
        profile.avatar.save(
            f'avatar-{profile.user.username}', ContentFile(image_data)
        )

    print('Avatars created successfully')
    print()


def generate_question_title(wrds_count=6):
    return fake.sentence(wrds_count)


def generate_question_content(par_count=5, sntc_count=8):
    content = ''
    while par_count > 0:
        content += fake.paragraph(sntc_count) + '\n'
        par_count -= 1
    return content


def create_questions(quest_count):
    print('Creating Questions')

    questions = []

    user_ids = models.Profile.objects.values_list('id', flat=True)

    with tqdm(total=quest_count) as pbar:
        with transaction.atomic(), ThreadPoolExecutor() as executor:
            while len(questions) < quest_count:
                author_id = random.choice(user_ids)

                question = models.Question(
                    title=generate_question_title(),
                    content=generate_question_content(),
                    author=models.Profile.objects.get(id=author_id),
                )
                questions.append(question)
                pbar.update(1)

                if len(questions) % BATCH_SIZE == 0:
                    models.Question.objects.bulk_create(questions)
                    quest_count -= len(questions)
                    questions = []
        
    if questions:
        models.Question.objects.bulk_create(questions)
    
    print('Questions created successfully')
    print()


def generate_answer_content(par_count=3, sntc_count=6):
    content = ''
    while par_count > 0:
        content += fake.paragraph(sntc_count) + '\n'
        par_count -= 1
    return content


def generate_answer_correct_flag(true_weight=0.2, false_weight=0.8):
    correct_flags = [True, False]
    correct_flags_weights = [true_weight, false_weight]
    return random.choices(correct_flags, correct_flags_weights)[0]


def create_answers(answ_count):
    print('Creating Answers')

    answers = []

    question_ids = models.Question.objects.values_list('id', flat=True)
    user_ids = models.Profile.objects.values_list('id', flat=True)

    with tqdm(total=answ_count) as pbar:
        with transaction.atomic(), ThreadPoolExecutor() as executor:
            while len(answers) < answ_count:
                question_id = random.choice(question_ids)
                author_id = random.choice(user_ids)

                answer = models.Answer(
                    content=generate_answer_content(),
                    correct_flag=generate_answer_correct_flag(),
                    question=models.Question.objects.get(id=question_id),
                    author=models.Profile.objects.get(id=author_id)
                )

                if answer.author != answer.question.author:
                    answers.append(answer)
                    pbar.update(1)

                    if len(answers) % BATCH_SIZE == 0:
                        models.Answer.objects.bulk_create(answers)
                        answ_count -= len(answers)
                        answers = []

    if answers:
        models.Answer.objects.bulk_create(answers)

    print('Answers created successfully')
    print()


def get_random_vote(like_weight, dislike_wieight):
    vote_type_choices = ['like', 'dislike']
    vote_type_weights = [like_weight, dislike_wieight]
    return random.choices(vote_type_choices, vote_type_weights)[0]


def create_likes(likes_target, likes_count,
                 like_weight=0.5, dislike_weight=0.5):
    print(f'Creating {likes_target.capitalize()} likes.')

    target_objects = {
        'questions': models.Question.objects.select_related('author__user'),
        'answers': models.Answer.objects.select_related('author__user'),
    }[likes_target]

    like_model = {
        'questions': models.QuestionLike,
        'answers': models.AnswerLike,
    }[likes_target]

    user_ids = models.Profile.objects.values_list('id', flat=True)
    target_ids = target_objects.values_list('id', flat=True)

    unique_pairs = set()
    likes = []

    with tqdm(total=likes_count) as pbar:
        with transaction.atomic(), ThreadPoolExecutor() as executor:
            while len(likes) < likes_count:
                user_id = random.choice(user_ids)
                target_id = random.choice(target_ids)

                if (target_id, user_id) not in unique_pairs:
                    unique_pairs.add((target_id, user_id))
                    target = target_objects.get(id=target_id)
                    user = models.Profile.objects.get(id=user_id)

                    if user.user == target.author.user:
                        continue

                    type = get_random_vote(like_weight, dislike_weight)

                    if likes_target == 'questions':
                        like = models.QuestionLike(
                            user=user,
                            question=target,
                            type=type,
                        )
                    elif likes_target == 'answers':
                        like = models.AnswerLike(
                            user=user,
                            answer=target,
                            type=type,
                        )

                    likes.append(like)
                    pbar.update(1)

                    if len(likes) % BATCH_SIZE == 0:
                        if likes_target == 'questions':
                            models.QuestionLike.objects.bulk_create(likes)
                        elif likes_target == 'answers':
                            models.AnswerLike.objects.bulk_create(likes)
                        
                        likes_count -= len(likes)
                        likes = []

    if likes:
        if likes_target == 'questions':
            models.QuestionLike.objects.bulk_create(likes)
        elif likes_target == 'answers':
            models.AnswerLike.objects.bulk_create(likes)

    print(f'{likes_target.capitalize()} likes created successfully')
    print()


def generate_tag_name():
    return fake.word()


def generate_tag():
    return models.Tag(
        tag_name=generate_tag_name(),
    )


def create_tags(tag_count):
    print('Creating Tags')

    tags = []
    tag_names = set()
    with tqdm(total=tag_count) as pbar:
        with transaction.atomic(), ThreadPoolExecutor() as executor:
            while len(tags) < tag_count:
                tag = generate_tag()

                if tag.tag_name not in tag_names:
                    tags.append(tag)
                    tag_names.add(tag.tag_name)
                    pbar.update(1)

    models.Tag.objects.bulk_create(tags)
    print('Tags created successfully')
    print()


def link_questions2tags(tags_per_question_max):
    print('Linking tags to Questions')

    quest_count = models.Question.objects.count()

    tag_ids = models.Tag.objects.values_list('id', flat=True)

    questions = models.Question.objects.all()

    with transaction.atomic(), ThreadPoolExecutor() as executor:
        for question in tqdm(questions):
            tags_per_question = random.randint(1, tags_per_question_max)

            selected_tag_ids = [random.choice(tag_ids)
                                for i in range(tags_per_question)]

            selected_tags = [models.Tag.objects.get(id=tag_id)
                            for tag_id in selected_tag_ids]
            
            question.tag.add(*selected_tags)

    print('Tags linked to Questions successfully')
    print()


def count_files(path):
    count = 0
    for _, _, files in os.walk(path):
        count += len(files)
    return count


def fill_data_base(ratio):
    PROFILES_COUNT = ratio
    QUESTIONS_COUNT = ratio * 10
    ANSWERS_COUNT = ratio * 100
    TAGS_COUNT = ratio
    VOTES_COUNT = ratio * 200
    AV_COUNT = count_files('avatars')
    TAGS_PER_QUESTION_MAX = 6

    create_users(PROFILES_COUNT)
    link_avatars2profiles(AV_COUNT)
    create_questions(ratio * 10)
    create_likes('questions', ratio * 100)
    create_answers(ratio * 100)
    create_likes('answers', ratio * 100)
    create_tags(ratio)
    link_questions2tags(TAGS_PER_QUESTION_MAX)

    print('Data Base filled')
