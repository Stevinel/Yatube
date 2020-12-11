from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from posts.models import Post
from posts.tests.test_settings import TestSettings


class PostURLTests(TestSettings):
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
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            text="Simple test text",
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )

    def test_accessibility_urls(self):
        """Тест работоспособности страниц"""
        patterns_and_codes = {
            reverse("index"): 200,
            reverse("group", args=[self.group.slug]): 200,
            reverse("profile", args=[self.user.username]): 200,
            reverse("post", args=[self.user.username, self.post.id]): 200,
            reverse(
                "add_comment", args=[self.user.username, self.post.id]
            ): 302,
            reverse(
                "del_comment",
                args=[self.user.username, self.post.id, self.comment.id],
            ): 302,
            reverse("profile_follow", args=[self.user.username]): 302,
            reverse("profile_unfollow", args=[self.user.username]): 302,
        }
        for pattern, code in patterns_and_codes.items():
            response = self.authorized_client.get(pattern)
            self.assertEqual(response.status_code, code)

    def test_accessibility_edit_post_url(self):
        """Тест страницы редактирования поста"""
        pattern = reverse("post_edit", args=[self.user.username, self.post.id])
        response_anonymous = self.anonymous_client.get(pattern)
        response_not_author = self.not_author.get(pattern)
        response_author = self.authorized_client.get(pattern)
        self.assertEqual(response_anonymous.status_code, 302)
        self.assertRedirects(
            response_not_author,
            reverse("post", args=[self.user.username, self.post.id]),
        )
        self.assertEqual(response_author.status_code, 200)

    def test_accessibility_new_post_url(self):
        """Тест страницы создания поста"""
        pattern = reverse("new_post")
        response_anonymous = self.anonymous_client.get(pattern)
        response_auth_client = self.authorized_client.get(pattern)
        self.assertRedirects(
            response_anonymous, reverse("login") + "?next=" + pattern
        )
        self.assertEqual(response_auth_client.status_code, 200)

    def test_404_error_url(self):
        """Сервер возвращает ошибку, если страница не найдена"""
        pattern = "404"
        response_anonymous = self.anonymous_client.get(pattern)
        response_auth_client = self.authorized_client.get(pattern)
        self.assertEqual(response_anonymous.status_code, 404)
        self.assertEqual(response_auth_client.status_code, 404)

    def test_img_on_pages_in_context(self):
        """При выводе поста с картинкой изображение передается в словаре
        context на: главную страницу, страницу профайла, страницу группы
        и на отдельную страницу поста
        """
        urls = {
            reverse("index"),
            reverse("profile", kwargs={"username": self.user}),
            reverse("group", kwargs={"slug": self.group.slug}),
        }
        for url in urls:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.context["page"][0].image, self.post.image
                )
        response = self.authorized_client.get(
            reverse(
                "post", kwargs={"username": self.user, "post_id": self.post.id}
            )
        )
        self.assertEqual(response.context["post"].image, self.post.image)
