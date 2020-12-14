from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post, User


class TestSettings(TestCase):
    @classmethod
    def setUpClass(cls):
        """Создание объектов.

        Объекты будут импортироваться в другие тесты"""
        super().setUpClass()
        cls.user = User.objects.create(
            username="Stevinel",
            first_name="Stan",
            last_name="Voronov",
        )
        cls.another_user = User.objects.create(
            username="nastyankins",
            first_name="Анастасия",
            last_name="Кузьмичёва",
        )
        cls.group = Group.objects.create(
            title="test",
            slug="test-group",
            description="some description",
        )
        cls.group2 = Group.objects.create(
            title="test2", slug="test-group2", description="some description2"
        )
        cls.user_not_author = User.objects.create(username="NotAuthor")
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый тест(рабочий)",
            group=cls.group,
        )

        for number in range(11):
            Post.objects.create(
                text="Some text", author=cls.user, group=cls.group
            )
        Post.objects.create(
            text="Some text", author=cls.user, group=cls.group2
        )

        site = Site.objects.get(id=1)
        flat_about = FlatPage.objects.create(
            url="/about-author/",
            title="about me",
            content="<b>some content</b>",
        )
        flat_tech = FlatPage.objects.create(
            url="/about-spec/",
            title="about my tech",
            content="<b>some content</b>",
        )
        flat_about.sites.add(site)
        flat_tech.sites.add(site)
        cls.static_pages = ("/about-author/", "/about-spec/")

    def setUp(self):
        super().setUp()
        self.anonymous_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.another_user)
        self.not_author = Client()
        self.not_author.force_login(self.user_not_author)
        cache.clear()
