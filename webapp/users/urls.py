# Django imports
from django.urls import path

from webapp.users.views import (
    RegisterUser,
    Login,
    Users
)

app_name = "users"
urlpatterns = [
    path("register", view=RegisterUser.as_view(), name="register"),
    path("login", view=Login.as_view(), name="login"),
    path("details", view=Users.as_view(), name="details"),

]
