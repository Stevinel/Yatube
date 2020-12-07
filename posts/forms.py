from django.forms import ModelForm, Select, Textarea
from django.forms.widgets import ClearableFileInput

from .models import Comment, Post


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
        fields = ("text",)
        widgets = {
            "text": Textarea(
                attrs={
                    "placeholder": "Введите текст комментария",
                    "class": "form-control",
                }
            )
        }
