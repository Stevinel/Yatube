from django.db.models.fields import CharField, SlugField
from django.forms import ModelForm, Select, Textarea
from django.forms.widgets import ClearableFileInput, TextInput

from .models import Comment, Group, Post, User


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ("group", "text", "image")
        widgets = {
            "group": Select(
                attrs={
                    "placeholder": "Выбор группы",
                    "class": "form-control",
                }
            ),
            "text": Textarea(
                attrs={
                    "placeholder": "Введите текст",
                    "class": "form-control",
                }
            ),
            "image": ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("text", "image")
        widgets = {
            "text": Textarea(
                attrs={
                    "placeholder": "Введите текст комментария",
                    "class": "form-control",
                }
            ),
            "image": ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ("title", "slug", "description")
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Название",
                    "class": "form-control",
                }
            ),
            "slug": TextInput(
                attrs={
                    "placeholder": "Введите слаг",
                    "class": "form-control",
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Введите небольшое описание группы",
                    "class": "form-control",
                }
            ),
        }

class UserEditForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
