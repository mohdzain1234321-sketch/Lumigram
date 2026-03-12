from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    author     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption    = models.TextField(blank=True)
    image      = models.ImageField(upload_to='posts/images/', blank=True, null=True)
    video      = models.FileField(upload_to='posts/videos/', blank=True, null=True)
    audio      = models.FileField(upload_to='posts/audio/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    filter_name = models.CharField(max_length=50, default='Normal')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Post by {self.author.username}'

    def like_count(self):
        return self.likes.count()


class Like(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)  # ← needed for likes over time chart

    class Meta:
        unique_together = ('user', 'post')


class Comment(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    post       = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.id}'


# ── Analytics Models ──────────────────────────────────────────

class PostView(models.Model):
    """Records every unique view of a post"""
    post      = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_views')
    viewer    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)


class PostAnalytics(models.Model):
    """Stores aggregated analytics per post"""
    post           = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='analytics')
    profile_visits = models.PositiveIntegerField(default=0)