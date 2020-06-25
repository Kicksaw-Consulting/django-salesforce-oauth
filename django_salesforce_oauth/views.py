import requests
import urllib

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.utils.crypto import get_random_string


def oauth(request: HttpRequest):
    domain = "test" if settings.USE_SANDBOX else "login"
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
    domain = "test" if settings.USE_SANDBOX else "login"
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

    token_data = response.json()

    from pprint import pprint

    pprint(token_data)

    sf_id_url = token_data.get("id")
    access_token = token_data.get("access_token")
    print(sf_id_url)
    response = requests.get(
        sf_id_url, headers={"Authorization": f"Bearer {access_token}"}
    )
    salesforce_user_data = response.json()

    username = salesforce_user_data.get("username")
    email = salesforce_user_data.get("email")
    # make a random password. We won't use it
    password = get_random_string(length=16)
    organization_id = salesforce_user_data.get("organization_id")

    User = get_user_model()

    try:
        user = User.objects.create_user(username, email, password)
    except IntegrityError:
        user = User.objects.get(username=username, email=email)

    login(request, user)

    messages.info(request, "Authentication with Salesforce successful!")

    return redirect("index")
