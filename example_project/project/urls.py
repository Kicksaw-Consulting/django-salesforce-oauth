from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("frontend.urls")),
    path("oauth/", include("django_salesforce_oauth.urls")),
    path("admin/", admin.site.urls),
]
