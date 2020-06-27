from django.contrib.auth import login
from django.shortcuts import redirect

from django_salesforce_oauth.utils import get_or_create_user


def oauth_callback(request, oauth):
    user = get_or_create_user(oauth)
    login(request, user)
    return redirect("index")
