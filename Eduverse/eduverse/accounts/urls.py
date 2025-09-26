from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (   # 👈 import your custom view explicitly
    signup_view,
    profile_view,
    profile_update_view,
    UserLoginView,
    delete_account_view, # <= important!
)

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", profile_view, name="profile"),
    path("profile/update/", profile_update_view, name="profile_update"),
    path("delete/", delete_account_view, name="delete_account"),
]