from askme import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from lorem.text import TextLorem
from random_username.generate import generate_username
import random
import string


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


def generate_user():
    username = generate_username()
    email = generate_email(username)
    password = generate_password(random.randint(8, 16))

    return User.objects.create_user(
        username=username,
        email=email,
        password=password
    )


def generate_profile():
    user = generate_user()
    profile = models.Profile(user=user)
    avatar_id = random.randint(1, 3)
    with open(f'avatars/avatar-{avatar_id}', 'rb') as image:
        image_data = image.read()
    
    profile.avatar.save(f'avatar-{user.useraname}', ContentFile(image_data))
    profile.save()



