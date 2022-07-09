from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from .models import Profile, Post, LikePost, FollowersCount
from django.contrib.auth.forms import AuthenticationForm
from itertools import chain
import random

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
import os
from twilio.rest import Client
# Create your views here.


@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_feed_list = []
    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(
        follower=request.user.username)

    user_post = FollowersCount.objects.filter(user=request.user.username)
    
    # order_by('-created_at')[:3]
    
    for users in user_post:
        user_feed_list.append(users.user)
        
    for user_feed in user_feed_list:
        feed_lists = Post.objects.filter(user=user_feed)
        feed.append(feed_lists)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(
        all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [x for x in list(
        new_suggestions_list) if (x not in list(current_user))]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(userid=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})


@login_required(login_url='signin')
def upload_post(request):
    if request.method == 'POST':
        user = request.user.username
        media = request.FILES.get('media')
        title = request.POST['title']
        caption = request.POST['caption']

        new_post = Post.objects.create(
            user=user, file=media, title=title, caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')


@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(
        post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.like_count = post.like_count + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.like_count = post.like_count - 1
        post.save()
        return redirect('/')


@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(userid=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(
                follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' + user)
        else:
            new_follower = FollowersCount.objects.create(
                follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        if request.FILES.get('image') == None:
            image = user_profile.image
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.image = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.image = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('settings')
    return render(request, 'setting.html', {'user_profile': user_profile})

def send_otp(number, message):
    account_sid = 'AC820a4ddc19a8b85043ca11fb08448a8c'
    auth_token = '125025d64807606380fe24d5e73b2323'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body="Your OTP Authentication Code", 
        from_='+19706388018', 
        to='+989036940804'
    )

    print(message.sid)

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        phone_number = request.POST['phone_number']
        request.session['username'] = username
        request.session['email'] = email
        request.session['password'] = password
        request.session['password2'] = password2
        request.session['phone_no'] = phone_number
        
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken')
                return redirect('signup')
            else:
                otp = random.randint(1000, 9999)
                request.session['otp'] = otp
                message = f'Your otp is {otp}'
                send_otp(phone_number, message)
                return redirect('otp-signup')
        else:
            messages.error(request, 'Passwords not matching')
            return redirect('signup')
        
    return render(request, 'signup.html')

def otpSignup(request):
    if request.method == 'POST':
        u_otp = request.POST['otp']
        otp = request.session.get('otp')
        username = request.session['username']
        email = request.session.get('email')
        phone_number = request.session.get('phone_no')
        password = request.session.get('password')
        
        hash_pwd = make_password(password)
        
        if int(u_otp) == otp:
            user = User.objects.create_user(username=username, email=email, 
                                            password=hash_pwd)
            user.save()
            user_instance = User.objects.get(username=username)
            user_profile = Profile.objects.create(user=user_instance, userid=user_instance.id, 
                                                phone_number=phone_number)
            user_profile.save()
            
            user_login = authenticate(username=username, password=password)
            auth_login(request, user_login)
            
            request.session.delete('otp')
            request.session.delete('username')
            request.session.delete('email')
            request.session.delete('phone_no')
            request.session.delete('password')
            
            messages.success(request, 'Registration Successfully Done !!')
            return redirect('settings')
        else:
            messages.error(request, 'Wrong OTP')
            # return redirect('signup')
        
    return render(request, 'otp-signup.html')

# def signup(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         email = request.POST['email']
#         password = request.POST['password']
#         password2 = request.POST['password2']

#         if password == password2:
#             if User.objects.filter(email=email).exists():
#                 messages.info(request, 'Email already taken')
#                 return redirect('signup')
#             elif User.objects.filter(username=username).exists():
#                 messages.info(request, 'Username already taken')
#                 return redirect('signup')
#             else:
#                 user = User.objects.create_user(
#                     username=username, email=email, password=password)
#                 user.save()

#                 user_login = authenticate(username=username, password=password)
#                 auth_login(request, user_login)

#                 user_model = User.objects.get(username=username)
#                 new_profile = Profile.objects.create(
#                     user=user_model, userid=user_model.id)
#                 new_profile.save()
#                 return redirect('settings')
#         else:
#             messages.info(request, 'Password not matching')
#             return redirect('signup')

#     return render(request, 'signup.html')

def signin(request):
    try:
        if request.session.get('failed') >= 3:
            return HttpResponse('You have to wait for 5 minutes to login again')
    except:
        request.session['failed'] = 0
        request.session.set_expiry(100)
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            request.session['username'] = username
            request.session['password'] = password
            u = User.objects.get(username=username)
            p = Profile.objects.get(user=u)
            p_number = p.phone_number
            otp = random.randint(1000, 9999)
            request.session['login_otp'] = otp
            message = f'Your otp is {otp}'
            send_otp(p_number, message)
            return redirect('otp-login')
        else:
            messages.error(request, 'Username or password is wrong !!')

    return render(request, 'signin.html')

def otpSignin(request):
    if request.method == 'POST':
        username = request.session['username']
        password = request.session['password']
        otp = request.session.get('login_otp')
        u_otp = request.POST['otp']
        
        if int(u_otp) == otp:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                request.session.delete('login_otp')
                messages.success(request, 'Login successfully')
                return redirect('/')
        else:
            messages.error(request, 'Wrong OTP')
            
    return render(request, 'otp-signin.html')  
                

# def signin(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']

#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             auth_login(request, user)
#             return redirect('/')
#         else:
#             messages.info(request, 'Account does not exist, please signup')
#             return redirect('signin')
#     else:
#         form = AuthenticationForm()

#     return render(request, 'signin.html', {'form': form})


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

def forget_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            uid = User.objects.get(email=email)
            host = request.get_host()
            url = f'http://{host}/change-password/{uid.profile.uuid}'
            
            send_mail(
                'Reset Password', 
                url, 
                settings.EMAIL_HOST_USER, 
                [email], 
                fail_silently=False, 
            )
            return redirect('forget-password-done')
        else:
            messages.error(request, 'email address does not exist')
    return render(request, 'forget-password.html')


def change_password(request, uid):
    try:
        if Profile.objects.filter(uuid=uid).exists():
            if request.method == 'POST':
                pass1 = request.POST['password1']
                pass2 = request.POST['password2']
                if pass1 == pass2:
                    p = Profile.objects.get(uuid=uid)
                    u = p.user
                    user = User.objects.get(username=u)
                    user.password = make_password(pass1)
                    user.save()
                    messages.success(request, f'Your password has been reset successfully')
                    return redirect('login')
                else:
                    messages.error('Two passwords did not match')
        else:
            return HttpResponse('Wrong reset password URL')            
    except:
        raise HttpResponse('Reset password URL does not exist')
    return render(request, 'change-password.html')


@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)
