from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid
import os

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
# Create your models here.


def validate_file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.jpg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


def get_profile_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '%s.%s' % (uuid.uuid4(), ext)
    return os.path.join(f'user/{instance.user.id}/profile_images/', filename)


def get_media_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = '%s.%s' % (uuid.uuid4(), ext)
    return os.path.join(f'user/{instance.user}/post_medias/', filename)

# def email_exist(value):
#     if User.objects.filter(email=value).exists():
#         raise ValidationError('A profile with this Email Address already exists')

phone_regex = RegexValidator(regex=r'^(\+98|0)?9\d{9}$', 
                             message="Phone number must be entered in the format: '+989999999999'. Up to 17 digits allowed.")

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    userid = models.IntegerField()
    image = models.ImageField(default='default.png', validators=[
                              validate_file_extension], upload_to=get_profile_file_path, null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    location = models.CharField(max_length=128, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=17, validators=[phone_regex], unique=True)

    def __str__(self) -> str:
        return self.user.username

# class Tag(models.Model):
#     creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')
#     name = models.CharField(unique=True, max_length=128)
#     created_at = models.DateTimeField(auto_now_add=True, blank=False)
#     updated_at = models.DateTimeField(auto_now=True, blank=False)

#     def __str__(self) -> str:
#         return f'{self.creator} {self.name}'


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=100, null=False, blank=False)
    file = models.ImageField(verbose_name='Media', upload_to=get_media_file_path, null=False, blank=False)
    caption = models.TextField(max_length=500, null=True, blank=True)
    # like = models.ManyToManyField(User, related_name='likers', blank=True)
    # tag = models.ManyToManyField(Tag, blank=True)
    # feed = models.ManyToManyField(User, blank=True)
    # comment_count = models.PositiveIntegerField(verbose_name='Total Comment', default=0)
    like_count = models.IntegerField(
        verbose_name='Total Like', default=0)
    user = models.CharField(max_length=128)
    profile = models.CharField(verbose_name='Uploader Profile', max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, blank=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
    
    def __str__(self) -> str:
        return f'{self.title} {self.caption[:12]} {self.user}'

    def get_absolute_url(self):
        return reverse("image_detail", kwargs={"pk": str(self.pk)})
        # args = [str(self.id)]


class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.username


class FollowersCount(models.Model):
    follower = models.CharField(max_length=128)
    user = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.user

# class Comment(models.Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
#     user = models.ForeignKey(User, verbose_name='Author', on_delete=models.CASCADE, related_name='comments', null=True)
#     email = models.EmailField()
#     text = models.TextField()
#     parent = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies', blank=True, null=True)
#     commented_at = models.DateTimeField(auto_now_add=True, blank=False)
#     active = models.BooleanField(default=False)

#     class Meta:
#         ordering = ['commented_at']

#     def __str__(self) -> str:
#         return f'Comment {self.text} by {self.user} with email ID: {self.email}'
