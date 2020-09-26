from django.contrib.auth import get_user_model

from django_salesforce_oauth.oauth import OAuth


def get_or_create_user(oauth: OAuth):
    """
    Accepts an OAuth object and retrieves a User, creating one if it doesn't exist
    """
    salesforce_id = oauth.id
    email = oauth.email
    password = oauth.password

    User = get_user_model()

    user = User.objects.filter(username=salesforce_id).first()

    if not user:
        user = User.objects.create_user(salesforce_id, email, password)

    return user
