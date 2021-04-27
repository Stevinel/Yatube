from django.urls import path

from . import views

urlpatterns = [
    path("new_group/", views.new_group, name="new_group"),
    path("group/<slug:slug>/", views.group_posts, name="group"),
    path("", views.index, name="index"),
    path("new/", views.new_post, name="new_post"),
    path("follow/", views.follow_index, name="follow_index"),
    path("<str:username>/", views.profile, name="profile"),
    path("<str:username>/<int:post_id>/", views.post_view, name="post"),
    path(
        "<str:username>/<int:post_id>/edit/", views.post_edit, name="post_edit"
    ),
    path(
        "<str:username>/<int:post_id>/comment/",
        views.add_comment,
        name="add_comment",
    ),
    path(
        "<str:username>/follow/", views.profile_follow, name="profile_follow"
    ),
    path(
        "<str:username>/unfollow/",
        views.profile_unfollow,
        name="profile_unfollow",
    ),
    path(
        "<str:username>/<int:post_id>/<int:comment_id>/delete",
        views.delete_comment,
        name="del_comment",
    ),
    path(
        "<str:username>/<int:post_id>/post_delete",
        views.post_delete,
        name="post_delete",
    ),
    path(
        "<str:username>/<int:post_id>/like",
        views.post_like,
        name="post_like",
    ),
    path(
        "<str:username>/<int:post_id>/unlike",
        views.post_unlike,
        name="post_unlike",
    ),
    path(
        "<str:username>/profile_edit", views.profile_edit, name="profile_edit"
    ),
]
