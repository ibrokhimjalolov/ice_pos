from django.urls import path
from . import api_views


urlpatterns = [
    path("user-detail/", api_views.UserDetail.as_view(), name="user-detail"),
]
