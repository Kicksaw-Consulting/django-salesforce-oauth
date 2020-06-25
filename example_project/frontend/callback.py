from django_salesforce_oauth.utils import get_or_create_user


def oauth_callback(request, oauth):
    return get_or_create_user(oauth)
