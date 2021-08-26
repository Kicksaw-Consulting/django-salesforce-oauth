import requests
import urllib

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.module_loading import import_string

from django_salesforce_oauth.oauth import OAuth
from django_salesforce_oauth.utils import get_or_create_user

CALLBACK_ERROR_MESSAGE = "CUSTOM_CALLBACK must return a user object or a redirect"

STATE_COOKIE_NAME = "django_salesforce_oauth_state"


def oauth(request, domain="login"):
    """
    View for initiating OAuth with Salesforce
    """
    url = f"https://{domain}.salesforce.com/services/oauth2/authorize"

    url_args = {
        "client_id": settings.SFDC_CONSUMER_KEY,
        "response_type": "code",
        "redirect_uri": settings.OAUTH_REDIRECT_URI,
        "scope": settings.SCOPES,
        # track whether or not this was a prod org, or a sandbox
        # this is separate from the state query param the user
        # may pass to this view.
        "state": domain,
    }
    args = urllib.parse.urlencode(url_args)

    url = f"{url}?{args}"

    response = redirect(url)
    state = request.GET.get("state")
    if state:
        response.set_cookie(STATE_COOKIE_NAME, value=state)
    return response


def oauth_callback(request):
    """
    View behind the callback URI provided to Salesforce
    """
    code = request.GET.get("code")
    state = request.GET.get("state")

    url = f"https://{state}.salesforce.com/services/oauth2/token"

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
        state = request.COOKIES.get(STATE_COOKIE_NAME)
        if state:
            response = custom_callback(request, oauth, state=state)
        else:
            response = custom_callback(request, oauth)
        is_user = type(response) == get_user_model()
        is_redirect = type(response) == HttpResponseRedirect
        assert is_user or is_redirect, CALLBACK_ERROR_MESSAGE
        if is_redirect:
            return response
        else:
            user = response
    else:
        user = get_or_create_user(oauth)

    login(request, user)

    messages.info(request, "Authentication with Salesforce successful!")

    return redirect(settings.LOGIN_REDIRECT_URL)
