# Quick start

Assuming you've already configured an app in your Salesforce instance to serve
as an OAuth provider, the following should get you up and running.

## Install

`pip install django-salesforce-oauth`

## Settings

Add the app to your `INSTALLED_APPS` in your django settings (`settings.py`):

```python
INSTALLED_APPS = [
    # ...
    "django_salesforce_oauth",
]
```

Add the following required variables to your `settings.py`:

```python
SCOPES = "YOUR SCOPES"  # space delimited, e.g., "id api refresh_token"
SFDC_CONSUMER_KEY = "YOUR KEY"
SFDC_CONSUMER_SECRET = "YOUR SECRET"
OAUTH_REDIRECT_URI = "{YOUR DOMAIN}/oauth/callback/"

# Optional, but Django provides a default you likely don't want
LOGIN_REDIRECT_URL = "/"
```

## Urls

Add `django-salesforce-oauth`'s urls to your main `urls.py`.

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path("oauth/", include("django_salesforce_oauth.urls")),
]
```

Then redirect sign-in requests to the `oauth` namespace.

### View example

```python
from django.shortcuts import redirect

def your_view(request):
    return redirect("oauth")  # or "oauth-sandbox"
```

### Template example

```html
<a href="{% url 'oauth' %}" class="btn btn-primary">Login</a>
```

# Advanced usage

## Custom callback

You likely will want to customize what happens after the OAuth flow is complete instead of simply
getting or creating a user. This can be done by specifying the following in your `settings.py`.

```python
CUSTOM_CALLBACK = "path.to.module.your_callback_function"
```

`your_callback_function` must accept the following two arguments:

1. the request object (useful in case you want to handle redirection yourself)
2. the OAuth object (contains all token and user data)

If you send the user to the `oauth` view with a query parameter called `state`, then you must
provide a third, optional argument to your custom callback function.

3. the state parameter. Only requered if you redirect to `oauth` with `?state=value` in your
   query params.

An example signature is:

```python
def your_callback_function(request, oauth, state=None):
    ...
```

If you do not return a redirect from `your_callback_function`, it's expected it will return
a user object. In this case the user will then be signed in and redirected to
`settings.LOGIN_REDIRECT_URL` (which you'll most likely want to set in your `settings.py`).

### Customizing the callback URI

By default the view behind the `oauth-callback` namespace, specified in the `django_salesforce_oauth`'s app's `urls.py`, is what needs to match `settings.OAUTH_REDIRECT_URI`.
But this can be customized by pointing it to some other url and registering the view wherever
you'd like it declared.

```python
# urls.py

from django_salesforce_oauth.views import oauth_callback

urlpatterns = [
    # ...
    # pass {"domain": "test"} to use a sandbox
    path("my/custom/url", oauth_callback, {"domain": "login"}, name="custom-oauth-callback"),
]
```

# Example project

The example project provides a full example of how to use this package,
but since it's an integration, there's a few steps to actually running it.

## SFDC

Configure a SFDC OAuth app with which you can OAuth against.

## .env

Place a `.env` file inside the `project` folder that contains the following keys
from the OAuth app you configured above:

```
SFDC_CONSUMER_KEY=some_key
SFDC_CONSUMER_SECRET=secret_stuff
```

## django

run migrations and start the server!

---

This project uses [poetry](https://python-poetry.org/) for dependency management
and packaging.
