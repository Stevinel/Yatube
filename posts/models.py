from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.expressions import Exists, OuterRef

User = get_user_model()


class PostQuerySet(models.Manager):
    def annotate_liked(self, user):
        return self.annotate(
            liked=Exists(
                Like.objects.filter(user=user.id, post_id=OuterRef("id")).only(
                    "id",
                ),
            ),
        )


class Post(models.Model):
    text = models.TextField(
        verbose_name="Введите текст",
        help_text="Введите текст вашего будущего поста",
    )
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    group = models.ForeignKey(
        "Group",
        verbose_name="Выберите группу",
        help_text="Выберите группу из существующих",
        related_name="posts",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    image = models.ImageField(
        verbose_name="Добавить фотографию",
        help_text="Вы можете прикрепить фотографию",
        upload_to="posts/",
        blank=True,
        null=True,
    )

    objects = PostQuerySet()

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="Заголовок",
        help_text="Название группы",
    )
    slug = models.SlugField(
        max_length=256,
        unique=True,
        verbose_name="Адрес",
        help_text="Адрес для группы. Например: 'novaya-gruppa'",
    )
    description = models.CharField(
        max_length=200, verbose_name="Описание", help_text="Описание группы"
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        verbose_name="Комментарий",
        related_name="comments",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        related_name="comments",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    text = models.TextField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
    verbose_name="Добавить фотографию",
    upload_to="comments/",
    blank=True,
    null=True,
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name="follower",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        User,
        related_name="following",    
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_follow"
            )
        ]


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="liker"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes"
    )

    class Meta:
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"], name="unique_like"
            )
        ]
