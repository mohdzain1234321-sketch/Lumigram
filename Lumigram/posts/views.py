from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .models import Post, Like, Comment, PostView, PostAnalytics
from .serializers import PostSerializer, CommentSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.utils import timezone

import base64, uuid
from django.core.files.base import ContentFile


# ── Create Post ───────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def create_post(request):
    caption             = request.data.get('caption', '')
    filter_name         = request.data.get('filter_name', 'Normal')
    filtered_image_data = request.data.get('filtered_image', '')

    post = Post(
        author      = request.user,
        caption     = caption,
        filter_name = filter_name,
        video       = request.FILES.get('video'),
        audio       = request.FILES.get('audio'),
    )

    if filtered_image_data and filtered_image_data.startswith('data:image'):
        fmt, imgstr = filtered_image_data.split(';base64,')
        ext         = fmt.split('/')[-1]
        post.image  = ContentFile(
            base64.b64decode(imgstr),
            name=f"{uuid.uuid4()}.{ext}"
        )
    elif request.FILES.get('image'):
        post.image = request.FILES.get('image')

    post.save()
    return Response(PostSerializer(post, context={'request': request}).data, status=201)


# ── Feed (posts from followed users) ──────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feed(request):
    following_users = request.user.profile.followers.values_list('id', flat=True)
    posts = Post.objects.filter(author_id__in=following_users)
    return Response(PostSerializer(posts, many=True, context={'request': request}).data)


# ── Like / Unlike ─────────────────────────────────────────────
@csrf_exempt
@api_view(['POST'])
def like_post(request, post_id):
    if not request.user.is_authenticated:
        return Response({'error': 'Login required'}, status=401)

    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()

    return Response({'like_count': post.likes.count()})


# ── Add Comment ───────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment = Comment.objects.create(
        user    = request.user,
        post    = post,
        content = request.data.get('content', '')
    )
    return Response(CommentSerializer(comment).data, status=201)


# ── Get Comments ──────────────────────────────────────────────
@api_view(['GET'])
def get_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.order_by('created_at')
    return Response(CommentSerializer(comments, many=True).data)


# ── List All Posts ────────────────────────────────────────────
@api_view(['GET'])
def all_posts(request):
    get_token(request)  # Ensure CSRF token is set for frontend
    posts = Post.objects.all().order_by('-created_at')

    if request.user.is_authenticated:
        for post in posts:
            PostView.objects.get_or_create(post=post, viewer=request.user)

    return Response(PostSerializer(posts, many=True, context={'request': request}).data)


# ── Post Detail ───────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return Response(PostSerializer(post, context={'request': request}).data)


# ── Post Analytics (author only) ──────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def post_analytics(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return Response({'error': 'Not authorized'}, status=403)

    period     = request.GET.get('period', '7d')
    period_map = {'24h': 1, '7d': 7, '30d': 30, 'all': 3650}
    days       = period_map.get(period, 7)
    since      = timezone.now() - timedelta(days=days)

    total_views = post.post_views.count()

    likes_over_time = (
        post.likes
        .filter(created_at__gte=since)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    comments_over_time = (
        post.comments
        .filter(created_at__gte=since)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    analytics, _ = PostAnalytics.objects.get_or_create(post=post)

    return Response({
        'views':              total_views,
        'likes':              post.likes.count(),
        'comments':           post.comments.count(),
        'profile_visits':     analytics.profile_visits,
        'likes_over_time':    list(likes_over_time),
        'comments_over_time': list(comments_over_time),
    })