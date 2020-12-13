import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from django.urls import reverse

from posts.models import Comment, Post
from posts.tests.test_settings import TestSettings


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class PostCreateFormTest(TestSettings):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_new_post(self):
        """Новый пост создаётся успешно"""
        posts_count = Post.objects.count()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        form_data = {
            "text": "Test.",
            "group": self.group.id,
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse("new_post"), data=form_data, follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data["group"])
        self.assertIsNotNone(response.context["post"].image)

    def test_edit_post(self):
        """Пост редактируется"""
        form_data = {
            "text": "modified text",
            "group": self.group.id,
        }
        self.authorized_client.post(
            reverse("post_edit", args=[self.user, self.post.id]),
            data=form_data,
            follow=True,
        )
        post = Post.objects.last()
        self.assertEqual(post.text, form_data["text"])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data["group"])

    def test_only_auth_user_can_add_comments(self):
        """Авторизированный пользователь может добавлять комментарии"""
        comments_count = Comment.objects.count()
        form_data = {"text": "Комментик"}
        self.authorized_client.post(
            reverse("add_comment", args=[self.user, self.post.id]),
            data=form_data,
            follow=True,
        )
        comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(comment.text, form_data["text"])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_not_auth_user_can_add_comments(self):
        """Невторизированный пользователь не может добавлять комментарии"""
        comments_count = Comment.objects.count()
        form_data = {"text": "коммент"}
        self.anonymous_client.post(
            reverse("add_comment", args=[self.user, self.post.id]),
            data=form_data,
            follow=True,
        )

        self.assertEqual(comments_count, Comment.objects.count())
