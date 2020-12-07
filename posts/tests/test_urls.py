from django.urls import reverse

from posts.tests.test_settings import TestSettings


class PostURLTests(TestSettings):
    def test_accessibility_urls(self):
        """Тест работоспособности страниц"""
        patterns_and_codes = {
            reverse("index"): 200,
            reverse("group", args=[self.group.slug]): 200,
            reverse("profile", args=[self.user.username]): 200,
            reverse("post", args=[self.user.username, self.post.id]): 200,
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
