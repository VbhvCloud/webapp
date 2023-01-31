# Django imports
from django.urls import path

from webapp.users.views import (
    RegisterUser,
    Login,
    Users
)

app_name = "users"
urlpatterns = [
    path("", view=RegisterUser.as_view(), name="register"),
    path("login", view=Login.as_view(), name="login"),
    path("<int:userId>", view=Users.as_view(), name="details"),

]
