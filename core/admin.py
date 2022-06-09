from django.contrib import admin
from .models import Post, Profile

# Register your models here.
admin.site.site_header = 'Social Media administration'
admin.site.index_title = 'social_media-app administration'
admin.site.site_title = 'Django site admin'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'file', 'caption',
                    'user', 'profile', 'created_at', 'updated_at']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'userid', 'image', 'bio', 'location']
    list_editable = ('user',)
    list_filter = ['user', 'userid']
    search_fields = ['user', 'image']
