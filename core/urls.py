from django.urls import path
from .views import *

urlpatterns = [
    path('signup', signup, name="signup"),
    path('signin', signin, name='signin'),
    path('logout', logout, name='logout'),
    path('', index, name='index'),
    path('upload-post', upload_post, name='upload-post'),
    path('settings', settings, name='settings'),
    path('search', search, name='search'),
    path('follow', follow, name='follow'),
    path('profile/<str:pk>', profile, name='profile'),
    path('like-post', like_post, name='like'),
]
