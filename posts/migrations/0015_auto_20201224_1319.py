# Generated by Django 3.1.4 on 2020-12-24 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_comment_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='comments/', verbose_name='Добавить фотографию'),
        ),
    ]
