from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [

    # -------------------------------------------------
    # Main pages
    # -------------------------------------------------

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "valuation/",
        views.valuation,
        name="valuation"
    ),

    path(
        "history/",
        views.history,
        name="history"
    ),

    path(
        "about/",
        views.about,
        name="about"
    ),


    # -------------------------------------------------
    # Authentication
    # -------------------------------------------------

    path(
        "signup/",
        views.signup,
        name="signup"
    ),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login"
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout"
    ),


    # -------------------------------------------------
    # Deleted valuation management
    # -------------------------------------------------

    path(
        "history/deleted/",
        views.deleted_history,
        name="deleted_history"
    ),

    path(
        "history/delete/<int:valuation_id>/",
        views.delete_valuation,
        name="delete_valuation"
    ),

    path(
        "history/restore/<int:valuation_id>/",
        views.restore_valuation,
        name="restore_valuation"
    ),

    path(
        "history/permanently-delete/<int:valuation_id>/",
        views.permanently_delete_valuation,
        name="permanently_delete_valuation"
    ),

]