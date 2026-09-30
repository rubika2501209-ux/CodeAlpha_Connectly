from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("post/create/", views.create_post, name="create_post"),
    path("post/<int:post_id>/like/", views.like_post, name="like_post"),
    path("post/<int:post_id>/comment/", views.comment_post, name="comment_post"),
    path("post/<int:post_id>/delete/", views.delete_post, name="delete_post"),

    path("user/<str:username>/", views.profile, name="profile"),
    path("user/<str:username>/follow/", views.follow_user, name="follow_user"),

    path("profile/edit/", views.edit_profile, name="edit_profile"),
]