from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.shortcuts import render

# GET /api/messages/
# Returns all conversations for the logged-in user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_conversations(request):
    convos = Conversation.objects.filter(participants=request.user)
    serializer = ConversationSerializer(
        convos,
        many=True,
        context={'request': request}  # needed for unread_count to know current user
    )
    return Response(serializer.data)


# POST /api/messages/start/
# Finds existing conversation between two users, or creates a new one
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_or_create_conversation(request):
    username = request.data.get('username')
    other_user = User.objects.get(username=username)

    # Check if a conversation already exists between these two users
    convo = Conversation.objects.filter(
        participants=request.user
    ).filter(participants=other_user).first()

    if not convo:
        convo = Conversation.objects.create()
        convo.participants.add(request.user, other_user)

    return Response(
        ConversationSerializer(convo, context={'request': request}).data
    )


# GET /api/messages/<id>/messages/
# Returns all messages in a conversation AND marks unread ones as seen
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, convo_id):
    convo = Conversation.objects.get(id=convo_id)

    # Mark all messages as seen (except ones sent by current user)
    convo.messages.filter(is_seen=False).exclude(
        sender=request.user
    ).update(is_seen=True)

    serializer = MessageSerializer(convo.messages.all(), many=True)
    return Response(serializer.data)


# POST /api/messages/<id>/send/
# Creates and saves a new message (text or media or both)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, convo_id):
    convo = Conversation.objects.get(id=convo_id)

    msg = Message.objects.create(
        conversation=convo,
        sender=request.user,
        content=request.data.get('content', ''),
    )

    if 'image' in request.FILES:
        msg.image = request.FILES['image']

    if 'video' in request.FILES:
        msg.video = request.FILES['video']

    msg.save()
    convo.save()  # updates 'updated_at' so this convo bubbles to top of list

    return Response(MessageSerializer(msg).data)
def messenger_page(request):
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('/login/')
    return render(request, 'messenger.html')
# POST /api/messages/share-post/
# Finds or creates a conversation with recipient, then sends the post as a message
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_post(request):
    from posts.models import Post

    recipient_username = request.data.get('recipient')
    post_id = request.data.get('post_id')

    if not recipient_username or not post_id:
        return Response({'error': 'recipient and post_id are required'}, status=400)

    try:
        recipient = User.objects.get(username=recipient_username)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)

    # Find or create conversation
    convo = Conversation.objects.filter(
        participants=request.user
    ).filter(participants=recipient).first()

    if not convo:
        convo = Conversation.objects.create()
        convo.participants.add(request.user, recipient)

    # Save message with shared_post FK (no ugly URL text)
    msg = Message.objects.create(
        conversation=convo,
        sender=request.user,
        content='',
        shared_post=post
    )
    convo.save()

    return Response({'success': True, 'message': f'Post shared with {recipient_username}'})
    convo = Conversation.objects.filter(
        participants=request.user
    ).filter(participants=recipient).first()

    if not convo:
        convo = Conversation.objects.create()
        convo.participants.add(request.user, recipient)

    # Send post link as a message
    msg = Message.objects.create(
        conversation=convo,
        sender=request.user,
        content=f"📷 Shared a post: {post_url}"
    )
    convo.save()  # bubbles convo to top of list

    return Response({'success': True, 'message': f'Post shared with {recipient_username}'})