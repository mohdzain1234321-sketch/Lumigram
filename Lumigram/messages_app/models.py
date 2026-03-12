from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='messages/images/', blank=True, null=True)
    video = models.FileField(upload_to='messages/videos/', blank=True, null=True)
    shared_post = models.ForeignKey(             # 👈 NEW
        'posts.Post',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='shared_in_messages'
    )
    is_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']