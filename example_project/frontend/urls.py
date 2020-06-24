from django.urls import path, include

from frontend.views import index

urlpatterns = [
    path("", index, name="index"),
]
