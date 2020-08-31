from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from django_salesforce_oauth.oauth import OAuth


def get_or_create_user(oauth: OAuth):
    """
    Accepts an OAuth object and retrieves a User, creating one if it doesn't exist
    """
    salesforce_id = oauth.id
    email = oauth.email
    password = oauth.password

    UserModel = get_user_model()

    try:
        user = UserModel.objects.create_user(salesforce_id, email, password)
    except IntegrityError:
        user = UserModel.objects.get(username=salesforce_id, email=email)
    return user
