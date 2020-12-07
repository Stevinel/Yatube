from django import forms
from django.urls import reverse

from posts.tests.test_settings import TestSettings


class PostPagesTests(TestSettings):
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse("index"): "index.html",
            reverse("group", args=[self.group.slug]): "group.html",
            reverse("new_post"): "new.html",
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
        self.assertIn("page", response.context)
        self.assertEqual(
            response.context["paginator"].page(1).object_list.count(), 10
        )

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("group", args=[self.group.slug])
        )
        self.assertEqual(response.context["group"], self.group)
        self.assertIn("page", response.context)
        self.assertEqual(
            response.context["paginator"].page(1).object_list.count(), 10
        )

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

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("profile", args=[self.user.username])
        )
        self.assertEqual(response.context["page"][0].author, self.user)
        self.assertIn("page", response.context)
        self.assertIn("user_profile", response.context)
        self.assertEqual(
            response.context["paginator"].page(2).object_list.count(), 3
        )
        self.assertIn("followers", response.context)
        self.assertIn("following", response.context)
        self.assertIn("is_following", response.context)

    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse("post", args=[self.user.username, self.post.id])
        )
        post = response.context["post"]
        self.assertIn("followers", response.context)
        self.assertIn("following", response.context)
        self.assertIn("is_following", response.context)
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
