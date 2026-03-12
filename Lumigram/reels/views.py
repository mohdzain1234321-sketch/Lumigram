from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from .models import Reel, ReelLike, ReelComment
from .serializers import ReelSerializer, ReelCommentSerializer

# ── Upload Reel ───────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def create_reel(request):
    reel = Reel(
        author  = request.user,
        caption = request.data.get('caption', ''),
        video   = request.FILES['video'],
        audio   = request.FILES.get('audio'),
    )
    reel.save()
    return Response(ReelSerializer(reel).data, status=201)

# ── List All Reels ────────────────────────────────────────────
@api_view(['GET'])
def list_reels(request):
    get_token(request)  # sets CSRF cookie
    reels = Reel.objects.all()
    return Response(ReelSerializer(reels, many=True).data)

# ── Like / Unlike Reel ────────────────────────────────────────
@csrf_exempt
@api_view(['POST'])
def like_reel(request, reel_id):
    if not request.user.is_authenticated:
        return Response({'error': 'Login required'}, status=401)
    reel = Reel.objects.get(id=reel_id)
    like, created = ReelLike.objects.get_or_create(user=request.user, reel=reel)
    if not created:
        like.delete()
    return Response({'like_count': reel.likes.count()})

# ── Add Comment ───────────────────────────────────────────────
@csrf_exempt
@api_view(['POST'])
def comment_reel(request, reel_id):
    if not request.user.is_authenticated:
        return Response({'error': 'Login required'}, status=401)
    reel = Reel.objects.get(id=reel_id)
    comment = ReelComment.objects.create(
        user    = request.user,
        reel    = reel,
        content = request.data.get('content', '')
    )
    return Response(ReelCommentSerializer(comment).data, status=201)

# ── List Reels by Username ────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reels(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response([], status=200)
    reels = Reel.objects.filter(author=user).order_by('-created_at')
    serializer = ReelSerializer(reels, many=True, context={'request': request})
    return Response(serializer.data)