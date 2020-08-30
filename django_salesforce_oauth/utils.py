from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


def get_or_create_user(oauth):
    """
    Accepts an OAuth object and retrieves a User, creating one if it doesn't exist
    """
    username = oauth.username
    email = oauth.email
    password = oauth.password

    UserModel = get_user_model()

    try:
        user = UserModel.objects.create_user(username, email, password)
    except IntegrityError:
        user = UserModel.objects.get(username=username, email=email)
    return user
