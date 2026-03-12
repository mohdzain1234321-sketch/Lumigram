from rest_framework import serializers
from .models import AudioTranscript
 
class AudioTranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioTranscript
        fields = ['id', 'audio_file', 'original_transcript',
                  'translated_text', 'target_language', 'created_at']
