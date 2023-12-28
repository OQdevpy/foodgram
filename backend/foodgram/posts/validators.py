import re

from django.core.exceptions import ValidationError


def validate_username(username):
    forbidden_symb = re.sub(r"^[\w.@+-]+\Z", ' ', username)
    if username == 'me':
        raise ValidationError('Недопустимое имя пользователя!')
    elif username in forbidden_symb:
        raise ValidationError(
            f"Не допустимые символы <{username}> в имени пользователя"
        )
    return username


def validate_slug(slug):
    if re.search(r'^[\w.@+-]+\Z', slug) is None:
        raise ValidationError(
            f'Не допустимые символы <{slug}> .'
        )
