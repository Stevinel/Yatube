from django.urls import reverse

from posts.models import Comment
from posts.tests.test_settings import TestSettings


class PostURLTests(TestSettings):
    def test_accessibility_urls(self):
        """Тест работоспособности страниц"""
        comment = Comment.objects.create(
            text="comment",
            author=self.user,
            post=self.post,
        )
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
                args=[self.user.username, self.post.id, comment.id],
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
