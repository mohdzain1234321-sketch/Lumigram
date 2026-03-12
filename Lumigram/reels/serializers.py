from rest_framework import serializers
from .models import Reel, ReelComment
from django.contrib.auth.models import User

class ReelAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username']

class ReelCommentSerializer(serializers.ModelSerializer):
    user = ReelAuthorSerializer(read_only=True)
    class Meta:
        model  = ReelComment
        fields = ['id', 'user', 'content', 'created_at']

class ReelSerializer(serializers.ModelSerializer):
    author     = ReelAuthorSerializer(read_only=True)
    comments   = ReelCommentSerializer(many=True, read_only=True)
    like_count = serializers.SerializerMethodField()

    class Meta:
        model  = Reel
        fields = ['id', 'author', 'caption', 'video', 'audio',
                  'like_count', 'comments', 'created_at']

    def get_like_count(self, obj):
        return obj.likes.count()