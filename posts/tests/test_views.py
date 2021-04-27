from django import forms
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from posts.models import Comment, Follow, Like, Post
from posts.tests.test_settings import TestSettings


class PostPagesTests(TestSettings):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            text="Simple test text",
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse("index"): "index.html",
            reverse("group", args=[self.group.slug]): "group.html",
            reverse("new_post"): "new.html",
            reverse("new_group"): "new_group.html",
            reverse(
                "post_edit", args=[self.user.username, self.post.id]
            ): "new.html",
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("index"))
        post = response.context["page"][0]
        self.assertEqual(post, self.post)
        self.assertEqual(len(response.context["paginator"].page(1)), 10)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("group", args=[self.group.slug])
        )
        self.assertEqual(response.context["group"], self.group)
        self.assertIn("page", response.context)
        self.assertEqual(len(response.context["paginator"].page(1)), 10)

    def test_new_page_show_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("new_post"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
            "image": forms.fields.ImageField,
        }
        for name, expected in form_fields.items():
            with self.subTest(name=name):
                field_filled = response.context.get("form").fields.get(name)
                self.assertIsInstance(field_filled, expected)

    def test_new_group_page_show_correct_context(self):
        """Шаблон new_group сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("new_group"))
        form_fields = {
            "title": forms.fields.CharField,
            "slug": forms.fields.SlugField,
            "description": forms.fields.CharField,
        }
        for name, expected in form_fields.items():
            with self.subTest(name=name):
                field_filled = response.context.get("form").fields.get(name)
                self.assertIsInstance(field_filled, expected)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("profile", args=[self.user.username])
        )
        self.assertEqual(response.context["page"][0].author, self.user)
        self.assertIn("page", response.context)
        self.assertIn("author", response.context)
        self.assertEqual(
            response.context["paginator"].page(2).object_list.count(), 4
        )
        self.assertIn("is_following", response.context)

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("post", args=[self.user.username, self.post.id])
        )
        post = response.context["post"]
        self.assertEqual(post, self.post)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("post_edit", args=[self.user.username, self.post.id])
        )
        self.assertIn("form", response.context)
        self.assertEqual(response.context["post"], self.post)

    def test_flatpages_show_correct_status_code(self):
        """Шаблоны flatpages возвращают ответ с правильным кодом статуса."""
        for url in self.static_pages:
            response = self.anonymous_client.get(url)
            with self.subTest():
                self.assertEqual(response.status_code, 200)

    def test_auth_user_can_follow_users(self):
        """Пользователь может подписываться на юзера"""
        self.authorized_client.post(
            reverse("profile_follow", args=[self.another_user]),
            follow=True,
        )
        follow = Follow.objects.first()
        self.assertEqual(Follow.objects.count(), 1)
        self.assertEqual(follow.author, self.another_user)
        self.assertEqual(follow.user, self.user)

    def test_auth_user_can_unfollow_users(self):
        """Пользователь может отписываться от юзера"""
        Follow.objects.create(
            user=self.user,
            author=self.another_user,
        )
        self.assertEqual(Follow.objects.count(), 1)
        self.authorized_client.post(
            reverse("profile_unfollow", args=[self.another_user]),
            follow=True,
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_comments_delete(self):
        """Комментарий удаляется"""
        comment = Comment.objects.create(
            text="comment",
            author=self.user,
            post=self.post,
        )
        self.authorized_client.post(
            reverse(
                "del_comment",
                args=[self.user.username, comment.post.id, comment.id],
            ),
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_post_delete(self):
        """Пост удаляется"""
        post_count = Post.objects.count()
        post = Post.objects.create(
            text="Удали меня", author=self.user, group=self.group
        )
        self.authorized_client.post(
            reverse(
                "post_delete",
                args=[self.user.username, post.id],
            ),
            follow=True,
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_new_post_created_on_page_followers(self):
        """Записи фолловеров.

        Новая запись пользователя появляется в ленте тех,
        кто на него подписан."""
        Follow.objects.create(
            user=self.user,
            author=self.another_user,
        )
        form_data = {
            "text": "Новый пост",
            "group": self.group.id,
            "author": self.another_user,
        }
        self.authorized_client2.post(
            reverse("new_post"),
            data=form_data,
            follow=True,
        )
        first_post = Post.objects.first()
        response = self.authorized_client.get(reverse("follow_index"))
        post = response.context["page"].object_list[0]
        self.assertEqual(post, first_post)

    def test_new_post_dont_show_on_unfollowers_page(self):
        """Записи фолловеров.

        Новая запись пользователя не появляется в ленте тех,
        кто НЕ подписан на него"""
        Follow.objects.create(
            user=self.user,
            author=self.another_user,
        )
        form_data = {
            "text": "Новый пост",
            "group": self.group.id,
            "author": self.another_user,
        }
        self.authorized_client2.post(
            reverse("new_post"),
            data=form_data,
            follow=True,
        )
        response = self.authorized_client2.get(reverse("follow_index"))
        posts = response.context["page"].object_list
        self.assertEqual(len(posts), 0)

    def test_cache(self):
        """Тест кэширования индекса"""
        client = self.authorized_client
        response = client.get(reverse("index"))
        content = response.content
        Post.objects.all().delete()
        response = client.get(reverse("index"))
        self.assertEqual(content, response.content, "Кеширование не работает")
        cache.clear()
        response = client.get(reverse("index"))
        self.assertNotEqual(
            content, response.content, "Кеширование неисправно"
        )

    def test_img_on_pages_in_context(self):
        """При выводе поста с картинкой изображение передается в словаре
        context на: главную страницу, страницу профайла, страницу группы
        и на отдельную страницу поста
        """
        urls = {
            "index": reverse("index"),
            "profile": reverse("profile", args=[self.user]),
            "group": reverse("group", args=[self.group.slug]),
            "post": reverse("post", args=[self.user, self.post.id]),
        }
        for name, url in urls.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertContains(response, "<img ")
                page = response.context.get("page")
                if page is not None:
                    image = page[0].image
                else:
                    image = response.context["post"].image
                self.assertEqual(image, self.post.image)

    def test_auth_user_can_add_like(self):
        """Пользователь может ставить лайк"""
        self.authorized_client.post(
            reverse("post_like", args=[self.user, self.post.id]),
            follow=True,
        )
        like = Like.objects.first()
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(like.user, self.user)

    def test_auth_user_can_delete_like(self):
        """Пользователь может убирать лайк"""
        Like.objects.create(
            user=self.user,
            post=self.post,
        )
        self.authorized_client.post(
            reverse("post_unlike", args=[self.user, self.post.id]),
            follow=True,
        )
        self.assertEqual(Like.objects.count(), 0)


    def test_new_group_show_correct_context(self):
        """Шаблон new_group сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("new_group"))
        form_fields = {
            "title": forms.fields.CharField,
            "slug": forms.fields.SlugField,
            "description": forms.fields.CharField,
        }
        for name, expected in form_fields.items():
            with self.subTest(name=name):
                field_filled = response.context.get("form").fields.get(name)
                self.assertIsInstance(field_filled, expected)