from rest_framework import serializers
from .models import Post, Like, Comment
from accounts.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author        = UserSerializer(read_only=True)
    comments      = CommentSerializer(many=True, read_only=True)
    like_count    = serializers.SerializerMethodField()
    is_liked      = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'caption', 'image', 'video', 'audio',
            'filter_name', 'like_count', 'is_liked', 'comment_count',
            'comments', 'created_at',
        ]

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_comment_count(self, obj):
        return obj.comments.count()