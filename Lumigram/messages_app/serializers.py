from rest_framework import serializers
from .models import Conversation, Message
from accounts.serializers import UserSerializer


class SharedPostSerializer(serializers.SerializerMethodField):
    pass


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    shared_post_data = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'content',
            'image',
            'video',
            'shared_post_data',   # 👈 NEW
            'is_seen',
            'created_at'
        ]

    def get_shared_post_data(self, obj):
        if not obj.shared_post:
            return None
        post = obj.shared_post
        return {
            'id': post.id,
            'image': post.image.url if post.image else None,
            'caption': post.caption or '',
            'author': post.author.username,
        }


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'last_message', 'unread_count', 'updated_at']

    def get_last_message(self, obj):
        msg = obj.messages.last()
        return MessageSerializer(msg).data if msg else None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request:
            return obj.messages.filter(is_seen=False).exclude(sender=request.user).count()
        return 0