from posts.tests.test_settings import TestSettings


class PostModelTest(TestSettings):
    def test_verbose_name(self):
        """Тест на verbose_name в моделе Post"""
        post = PostModelTest.post
        field_verboses = {
            "text": "Введите текст",
            "group": "Выберите группу",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """Тест на help_text в моделе Post"""
        post = PostModelTest.post
        field_help_text = {
            "text": "Введите текст вашего будущего поста",
            "group": "Выберите группу из существующих",
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected
                )

    def test_method_str(self):
        """Тест метода str модели Post"""
        post = PostModelTest.post
        text = post.text
        self.assertEqual(str(post), text[:15])


class GroupModelTest(TestSettings):
    def test_verbose_name(self):
        """Тест на verbose_name в моделе Group"""
        group = GroupModelTest.group
        field_verboses = {
            "title": "Заголовок",
            "slug": "Слаг",
            "description": "Описание",
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected
                )

    def test_help_text(self):
        """Тест на help_text в моделе Group"""
        group = GroupModelTest.group
        field_help_text = {
            "title": "Название группы",
            "slug": "Адрес для страницы с группой",
            "description": "Описание группы",
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected
                )

    def test_method_str(self):
        """Тест метода str модели Group"""
        group = GroupModelTest.group
        title = group.title
        self.assertEqual(str(group), title)
