from django.db import models
from django.contrib.auth.models import User

class Reel(models.Model):
    author     = models.ForeignKey(User, on_delete=models.CASCADE)
    caption    = models.TextField(blank=True)
    video      = models.FileField(upload_to='reels/videos/')
    audio      = models.FileField(upload_to='reels/audio/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Reel by {self.author.username}'

class ReelLike(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE)
    reel  = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='likes')
    class Meta:
        unique_together = ('user', 'reel')

class ReelComment(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    reel       = models.ForeignKey(Reel, on_delete=models.CASCADE, related_name='comments')
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)