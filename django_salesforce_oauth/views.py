import requests
import urllib

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.db.utils import IntegrityError

from django_salesforce_oauth.oauth import OAuth
from django_salesforce_oauth.utils import get_salesforce_domain


def oauth(request: HttpRequest):
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


def oauth_callback(request: HttpRequest):
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

    username = oauth.username
    email = oauth.email
    password = oauth.password

    UserModel = get_user_model()

    try:
        user = UserModel.objects.create_user(username, email, password)
    except IntegrityError:
        user = UserModel.objects.get(username=username, email=email)

    login(request, user)

    messages.info(request, "Authentication with Salesforce successful!")

    return redirect("index")
