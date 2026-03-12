from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile
 
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'bio', 'photo', 'website', 'follower_count', 
                  'following_count', 'is_private', 'push_notifications', 
                  'email_notifications']
 
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
 
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
 
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
 
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
 
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
