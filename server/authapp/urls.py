from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("signup/", views.signup_user),
    path("login/", obtain_auth_token),
    path("api/logout/", views.logout_view, name="logout"),
]
