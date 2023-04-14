from askme import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from faker import Faker
from faker.providers import internet, lorem
import random
import string
from tqdm import tqdm


Faker.seed(0)
fake = Faker()


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

    return User.objects.create_user(
        username=username,
        email=email,
        password=password
    )


def generate_profile():
    user = generate_user()
    profile = models.Profile(user=user)

    return profile


def generate_question_title(wrds_count=6):
    return fake.sentence(wrds_count)


def generate_question_content(par_count=5, sntc_count=8):
    content = ''
    while par_count > 0:
        content += fake.paragraph(sntc_count) + '\n'
        par_count -= 1
    return content


def get_random_instances(objects, objects_count=1):
    return objects.order_by('?')[:objects_count]


def generate_question():
    return models.Question(
        title=generate_question_title(),
        content=generate_question_content(),
        author=get_random_instances(models.Profile.objects).get(),
    )


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


def generate_answer():
    content = generate_answer_content()
    correct_flag = generate_answer_correct_flag()
    question = get_random_instances(models.Question.objects).get()
    while True:
        author = get_random_instances(models.Profile.objects).get()
        if author != question.author:
            break

    return models.Answer(
        content=content,
        correct_flag=correct_flag,
        question=question,
        author=author,
    )


def generate_tag_name():
    return fake.word()


def generate_tag():
    return models.Tag(
        tag_name=generate_tag_name(),
    )


def get_random_vote(like_weight, dislike_wieight):
    vote_type_choices = ['like', 'dislike']
    vote_type_weights = [like_weight, dislike_wieight]
    return random.choices(vote_type_choices, vote_type_weights)[0]


def generate_question_like(like_weight=0.5, dislike_wieight=0.5):
    while True:
        user = get_random_instances(models.Profile.objects).get()
        question = get_random_instances(models.Question.objects).get()

        if (question, user) not in generate_question_like.q_u_pairs and \
            not models.QuestionLike.objects.filter(
            user=user,
            question=question,
        ).exists():
            generate_question_like.q_u_pairs.append((question, user))
            type = get_random_vote(like_weight, dislike_wieight)

            return models.QuestionLike(
                user=user,
                question=question,
                type=type
            )


generate_question_like.q_u_pairs = []


def generate_answer_like(like_weight=0.4, dislike_wieight=0.3):
    while True:
        user = get_random_instances(models.Profile.objects).get()
        answer = get_random_instances(models.Answer.objects).get()

        if (answer, user) not in generate_answer_like.a_u_pairs and \
            not models.AnswerLike.objects.filter(
            user=user,
            answer=answer,
        ).exists():
            if answer.correct_flag:
                type = get_random_vote(0.9, 0.1)
            else:
                type = get_random_vote(like_weight, dislike_wieight)

            generate_answer_like.a_u_pairs.append((answer, user))

            return models.AnswerLike(
                user=user,
                answer=answer,
                type=type
            )


generate_answer_like.a_u_pairs = []


def create_profiles(prof_count, batch_size):
    batch_size = min(batch_size, prof_count)
    print('Creating profiles.')
    for i in tqdm(range(prof_count)):
        if i % batch_size == 0:
            models.Profile.objects.bulk_create(
                [generate_profile() for i in range(batch_size)]
            )

    print()


def get_random_avatar(av_id_from=1, av_id_to=10):
    avatar_id = random.randint(av_id_from, av_id_to)
    with open(f'avatars/avatar-{avatar_id}.jpg', 'rb') as image:
        image_data = image.read()

    return image_data


def link_avatars2profiles(batch_size, av_count):
    print('Creating profle avatars.')
    prof_count = models.Profile.objects.count()
    batch_size = min(batch_size, prof_count)
    start_pos, end_pos = 0, batch_size
    for i in tqdm(range(prof_count)):
        if i % batch_size == 0:
            end_pos = min(end_pos, prof_count)

            profiles = models.Profile.objects.all()[start_pos:end_pos]
            start_pos += batch_size
            end_pos += batch_size
            for profile in models.Profile.objects.all():
                image_data = get_random_avatar(av_id_to=av_count - 1)
                profile.avatar.save(
                    f'avatar-{profile.user.username}', ContentFile(image_data)
                )

    print()


def create_questions(quest_count, batch_size):
    batch_size = min(batch_size, quest_count)
    print('Creating questions.')
    for i in tqdm(range(quest_count)):
        if i % batch_size == 0:
            models.Question.objects.bulk_create(
                [generate_question() for i in range(batch_size)]
            )

    print()


def create_question_likes(likes_count, batch_size):
    batch_size = min(batch_size, likes_count)
    print('Creating question likes.')
    for i in tqdm(range(likes_count)):
        if i % batch_size == 0:
            models.QuestionLike.objects.bulk_create(
                [generate_question_like() for i in range(batch_size)]
            )
            generate_question_like.q_u_pairs = []

    print()


def create_answers(answ_count, batch_size):
    batch_size = min(batch_size, answ_count)
    print('Creating answers.')
    for i in tqdm(range(answ_count)):
        if i % batch_size == 0:
            models.Answer.objects.bulk_create(
                [generate_answer() for i in range(batch_size)]
            )

    print()


def create_answer_likes(likes_count, batch_size):
    batch_size = min(batch_size, likes_count)
    print('Creating answer likes')
    for i in tqdm(range(likes_count)):
        if i % batch_size == 0:
            models.AnswerLike.objects.bulk_create(
                [generate_answer_like() for i in range(batch_size)]
            )
            generate_answer_like.a_u_pairs = []

    print()


def create_tags(tag_count, batch_size):
    batch_size = min(batch_size, tag_count)
    print('Creating tags.')
    for i in tqdm(range(tag_count)):
        if i % batch_size == 0:
            models.Tag.objects.bulk_create(
                [generate_tag() for i in range(batch_size)]
            )

    print()


def link_questions2tags(tags_per_question_max, batch_size):
    print('Linking tags to questions.')
    quest_count = models.Question.objects.count()
    batch_size = min(batch_size, quest_count)
    start_pos, end_pos = 0, batch_size
    for i in tqdm(range(quest_count)):
        if i % batch_size == 0:
            end_pos = min(end_pos, quest_count)

            questions = models.Question.objects.all()[start_pos:end_pos]
            start_pos += batch_size
            end_pos += batch_size
            for question in questions:
                tags_per_question = random.randint(1, tags_per_question_max)
                question.tag.add(
                    *get_random_instances(models.Tag.objects, tags_per_question)
                )

    print()


def fill_data_base(ratio):
    PROFILES_COUNT = ratio
    QUESTIONS_COUNT = ratio * 10
    ANSWERS_COUNT = ratio * 100
    TAGS_COUNT = ratio
    VOTES_COUNT = ratio * 200
    BATCH_SIZE = 100
    AV_COUNT = 219
    TAGS_PER_QUESTION_MAX = 6

    create_profiles(ratio, BATCH_SIZE)
    link_avatars2profiles(BATCH_SIZE, AV_COUNT)
    create_questions(ratio * 10, BATCH_SIZE)
    create_question_likes(ratio * 100, BATCH_SIZE)
    create_answers(ratio * 100, BATCH_SIZE)
    create_answer_likes(ratio * 100, BATCH_SIZE)
    create_tags(ratio, BATCH_SIZE)
    link_questions2tags(TAGS_PER_QUESTION_MAX, BATCH_SIZE)

    print('Data Base filled')
