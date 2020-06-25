from django.contrib.auth.views import LogoutView
from django.urls import path

from django_salesforce_oauth.views import oauth, oauth_callback

urlpatterns = [
    path("", oauth, name="oauth"),
    path("callback/", oauth_callback, name="oauth-callback"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
