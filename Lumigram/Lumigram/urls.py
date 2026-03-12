from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect
from messages_app import views as msg_views

# Simple frontend views
def home(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, 'feed.html')

def reels_page(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, 'reels.html')

def login_page(request):
    if request.user.is_authenticated:
        return redirect(f'/profile/{request.user.username}/')
    return render(request, 'login.html')

def register_page(request):                          # ✅ NEW
    if request.user.is_authenticated:
        return redirect(f'/profile/{request.user.username}/')
    return render(request, 'register.html')

def explore_page(request):
    return render(request, 'explore.html')

def user_profile_page(request, username):
    return render(request, 'user_profile.html')

def profile_page(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return redirect(f'/profile/{request.user.username}/')

def profile_page_username(request, username):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, 'profile.html')

def post_detail_page(request, post_id):
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, 'post_detail.html', {'post_id': post_id})


urlpatterns = [
    path('admin/',     admin.site.urls),

    # Frontend pages
    path('',                         home,                     name='home'),
    path('reels/',                   reels_page,               name='reels-page'),
    path('messenger/',               msg_views.messenger_page, name='messenger'),
    path('login/',                   login_page,               name='login'),
    path('register/',                register_page,            name='register'),  # ✅ NEW
    path('explore/',                 explore_page,             name='explore'),
    path('user/<str:username>/',     user_profile_page,        name='user_profile'),
    path('posts/<int:post_id>/',     post_detail_page,         name='post_detail'),

    # Profile URLs
    path('profile/',                 profile_page,             name='profile_redirect'),
    path('profile/<str:username>/',  profile_page_username,    name='profile_page'),

    # API routes
    path('api/accounts/', include('accounts.urls')),
    path('api/posts/',    include('posts.urls')),
    path('api/reels/',    include('reels.urls')),
    path('api/audio/',    include('audio_features.urls')),
    path('api/messages/', include('messages_app.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)