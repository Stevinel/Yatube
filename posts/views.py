from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


@cache_page(10)
def index(request):
    """Функция главной страницы"""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request, "index.html", {"page": page, "paginator": paginator}
    )


def group_posts(request, slug):
    """Фунция страницы групп"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {"group": group, "page": page, "paginator": paginator}
    return render(request, "group.html", context)


@login_required
def new_post(request):
    """Функция страницы создания нового поста"""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")

    context = {
        "form": form,
        "is_new_post": True,
    }
    return render(request, "new.html", context)


def profile(request, username):
    """Функция страницы профиля"""
    author = get_object_or_404(User, username=username)
    post = author.posts.all()
    paginator = Paginator(post, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    is_following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    )
    context = {
        "page": page,
        "paginator": paginator,
        "author": author,
        "is_following": is_following,
    }
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    """Функция страницы поста"""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    comments = post.comments.all()
    form = CommentForm()
    return render(
        request,
        "post.html",
        {
            "form": form,
            "post": post,
            "comments": comments,
        },
    )


@login_required
def post_edit(request, username, post_id):
    """Функция редактирования поста"""
    post = get_object_or_404(Post, id=post_id, author__username=username)

    if post.author != request.user:
        return redirect("post", username, post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )

    if form.is_valid():
        post.save()
        return redirect("post", username, post_id)

    context = {
        "form": form,
        "post": post,
    }
    return render(request, "new.html", context)


def page_not_found(request, exception):
    """Функция страницы 404"""
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    """Функция страницы 500"""
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    """Функция добавления комментария"""
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("post", username, post_id)


@login_required
def delete_comment(request, username, post_id, comment_id):
    """Функция удаления комментария юзером"""
    comment = get_object_or_404(Comment, pk=comment_id, post=post_id)
    if comment.author == request.user:
        comment.delete()
    return redirect("post", username, post_id)


@login_required
def follow_index(request):
    """Функция страницы подписок"""
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    form = PostForm()
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "page": page,
        "paginator": paginator,
        "form": form,
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    """Функция подписки на автора"""
    author = get_object_or_404(User, username=username)
    if (
        author == request.user
        or Follow.objects.filter(author=author, user=request.user).exists()
    ):
        return redirect("profile", username=username)

    Follow.objects.create(
        user=request.user,
        author=author,
    )
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    """Функция отписки от автора"""
    user = request.user
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=user, author=author)
    if follow.exists():
        follow.delete()

    return redirect("profile", username)
