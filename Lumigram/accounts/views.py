from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from reels.models import Reel
from posts.models import Post
from .models import Profile
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer
from django.shortcuts import render

# ── Register ──────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({'message': 'Account created!'}, status=201)
    return Response(serializer.errors, status=400)

# ── Login ─────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        # ✅ FIX 1: Return username so frontend can redirect to correct profile URL
        return Response({'message': 'Login successful!', 'username': user.username})
    return Response({'error': 'Invalid credentials'}, status=400)

# ── Logout ────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({'message': 'Logged out'})

# ✅ FIX 2: New /me/ endpoint — returns the currently logged-in user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# ── Get / Edit Profile ────────────────────────────────────────
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request, username):
    user = User.objects.get(username=username)
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    if request.method == 'PUT' and request.user == user:
        profile = user.profile
        profile.bio     = request.data.get('bio', profile.bio)
        profile.website = request.data.get('website', profile.website)
        profile.is_private = request.data.get('is_private', str(profile.is_private)).lower() == 'true'
        profile.push_notifications = request.data.get('push_notifications', str(profile.push_notifications)).lower() == 'true'
        profile.email_notifications = request.data.get('email_notifications', str(profile.email_notifications)).lower() == 'true'
        if 'photo' in request.FILES:
            profile.photo = request.FILES['photo']
        profile.save()
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name  = request.data.get('last_name', user.last_name)
        user.save()
        return Response({'message': 'Profile updated!'})
    return Response({'error': 'Forbidden'}, status=403)

# ── Change Password ───────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    if not user.check_password(old_password):
        return Response({'error': 'Current password is incorrect'}, status=400)
    if len(new_password) < 8:
        return Response({'error': 'Password must be at least 8 characters'}, status=400)
    user.set_password(new_password)
    user.save()
    login(request, user)
    return Response({'message': 'Password changed successfully!'})

# ── Follow / Unfollow ─────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_unfollow(request, username):
    target = User.objects.get(username=username)
    profile = target.profile
    if request.user in profile.followers.all():
        profile.followers.remove(request.user)
        return Response({'message': 'Unfollowed'})
    profile.followers.add(request.user)
    return Response({'message': 'Followed'})

# ── Search Users ──────────────────────────────────────────────
@api_view(['GET'])
def search_users(request):
    query = request.query_params.get('q', '')
    users = User.objects.filter(username__icontains=query)[:10]
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

# ── Profile Page (HTML render) ────────────────────────────────
def profile_page(request, username):
    profile_user = User.objects.get(username=username)
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    reels = Reel.objects.filter(author=profile_user).order_by('-created_at')
    
def register_page(request):
    return render(request, 'register.html')

    is_following = False
    if request.user.is_authenticated:
        is_following = request.user in profile_user.profile.followers.all()

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'reels': reels,
        'is_following': is_following,
        'posts_count': posts.count(),
        'followers_count': profile_user.profile.followers.count(),
        'following_count': User.objects.filter(profile__followers=profile_user).count(),
    })