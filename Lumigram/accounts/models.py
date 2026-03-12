from django.db import models
from django.contrib.auth.models import User
 
class Profile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    bio        = models.TextField(blank=True)
    photo      = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    website    = models.URLField(blank=True)
    followers  = models.ManyToManyField(User, related_name='following', blank=True)
    is_private        = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.username} Profile'
 
    def follower_count(self):
        return self.followers.count()
 
    def following_count(self):
        return Profile.objects.filter(followers=self.user).count()
 
# Auto-create Profile when User registers
from django.db.models.signals import post_save
from django.dispatch import receiver
 
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
 
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
