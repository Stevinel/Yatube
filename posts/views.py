from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models.expressions import Exists, OuterRef

from django.db.models.query import QuerySet
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from users.forms import CreationForm

from .forms import CommentForm, GroupForm, PostForm, UserEditForm
from .models import Comment, Follow, Group, Like, Post, User



@cache_page(1)
def index(request):
    """Функция главной страницы"""
    search_query = request.GET.get("search", "",)
    if search_query:
        post_list = Post.objects.filter(text__icontains=search_query)
    else:
        post_list = Post.objects.annotate_liked(request.user).all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request, "index.html", {"page": page, "paginator": paginator,}
    )



def group_posts(request, slug):
    """Фунция страницы групп"""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.annotate_liked(request.user).all()
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
    post = author.posts.annotate_liked(request.user).all()
    paginator = Paginator(post, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    is_following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
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
    post = get_object_or_404(
        Post.objects.annotate_liked(request.user),
        id=post_id,
        author__username=username,
    )
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
    form = CommentForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("post", username, post_id)


@login_required
def delete_comment(request, username, post_id, comment_id):
    """Функция удаления комментария юзером"""
    comment = get_object_or_404(Comment, id=comment_id, post=post_id)
    if comment.author == request.user:
        comment.delete()
    return redirect("post", username, post_id)


@login_required
def follow_index(request):
    """Функция страницы подписок"""
    post_list = Post.objects.annotate_liked(request.user).filter(
        author__following__user=request.user
    )
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


@login_required
def post_delete(request, username, post_id):
    """Функция удаления поста"""
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        post.delete()
    return redirect("profile", username=username)


@login_required
def post_like(request, username, post_id):
    """"Функция лайка"""
    post = get_object_or_404(Post, author__username=username, id=post_id)
    Like.objects.get_or_create(post=post, user=request.user)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def post_unlike(request, username, post_id):
    """"Функция АНлайка"""
    post = get_object_or_404(Post, author__username=username, id=post_id)
    post.likes.filter(user=request.user).delete()
    return HttpResponseRedirect(
        request.META.get(
            "HTTP_REFERER",
            "/",
        )
    )


@login_required
def new_group(request):
    """Функция страницы создания новой группы"""
    form = GroupForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")
    context = {
        "form": form,
    }
    return render(request, "new_group.html", context)


@login_required
def profile_edit(request, username):
    """"Функция редактирования профиля"""
    user_profile = get_object_or_404(User, username=username)
    if request.user != user_profile:
        return redirect('profile', username=user_profile.username)
    form = UserEditForm(request.POST or None, instance=user_profile)
    if form.is_valid():
        form.save()
        return redirect('profile', username=user_profile.username)
    return render(request, 'profile_edit.html', {'form': form})

    