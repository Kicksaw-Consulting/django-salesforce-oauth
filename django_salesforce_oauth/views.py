import requests
import urllib

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.module_loading import import_string

from django_salesforce_oauth.oauth import OAuth
from django_salesforce_oauth.utils import get_salesforce_domain, get_or_create_user

CALLBACK_ERROR_MESSAGE = (
    "Please return a valid user object or provide your own redirect for CUSTOM_CALLBACK"
)


def oauth(request):
    domain = get_salesforce_domain()
    url = f"https://{domain}.salesforce.com/services/oauth2/authorize"

    url_args = {
        "client_id": settings.SFDC_CONSUMER_KEY,
        "response_type": "code",
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "scope": settings.SCOPES,
    }
    args = urllib.parse.urlencode(url_args)

    url = f"{url}?{args}"

    return redirect(url)


def oauth_callback(request):
    domain = get_salesforce_domain()
    url = f"https://{domain}.salesforce.com/services/oauth2/token"

    code = request.GET.get("code")

    if not code:
        messages.error(request, "Unable to authenticate with Salesforce")
        return redirect("index")

    data = {
        "client_id": settings.SFDC_CONSUMER_KEY,
        "client_secret": settings.SFDC_CONSUMER_SECRET,
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "grant_type": "authorization_code",
        "code": code,
    }
    response = requests.post(url, data)

    oauth = OAuth(response.json())

    if hasattr(settings, "CUSTOM_CALLBACK"):
        custom_callback = import_string(settings.CUSTOM_CALLBACK)
        user = custom_callback(request, oauth)
        assert type(user) == get_user_model(), CALLBACK_ERROR_MESSAGE
    else:
        user = get_or_create_user(oauth)

    login(request, user)

    messages.info(request, "Authentication with Salesforce successful!")

    return redirect(settings.LOGIN_REDIRECT_URL)
