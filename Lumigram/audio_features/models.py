from django.db import models
from django.contrib.auth.models import User
 
class AudioTranscript(models.Model):
    user             = models.ForeignKey(User, on_delete=models.CASCADE)
    audio_file       = models.FileField(upload_to='audio_transcripts/')
    original_transcript = models.TextField(blank=True)   # Transcribed text
    translated_text  = models.TextField(blank=True)      # Translated text
    target_language  = models.CharField(max_length=50, blank=True)  # e.g. 'hindi'
    created_at       = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f'Transcript by {self.user.username} at {self.created_at}'
