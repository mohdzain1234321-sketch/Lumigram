import os
import speech_recognition as sr
from pydub import AudioSegment
from deep_translator import GoogleTranslator
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django.conf import settings
from .models import AudioTranscript
from .serializers import AudioTranscriptSerializer
from django.contrib.auth.models import User
 
 
def convert_to_wav(audio_path):
    """Convert any audio file to WAV format for SpeechRecognition."""
    wav_path = audio_path.rsplit('.', 1)[0] + '_converted.wav'
    audio = AudioSegment.from_file(audio_path)
    audio.export(wav_path, format='wav')
    return wav_path
 
 
def transcribe_audio(audio_path):
    """Convert audio to text using SpeechRecognition library."""
    recognizer = sr.Recognizer()
    # Convert to WAV if needed
    if not audio_path.endswith('.wav'):
        audio_path = convert_to_wav(audio_path)
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data)  # Uses Google API
        return text
    except sr.UnknownValueError:
        return 'Could not understand the audio'
    except sr.RequestError as e:
        return f'API Error: {e}'
 
 
def translate_text(text, target_language):
    """Translate text to target language using deep-translator."""
    try:
        translated = GoogleTranslator(
            source='auto',
            target=target_language
        ).translate(text)
        return translated
    except Exception as e:
        return f'Translation error: {e}'
 
 
# ── API View: Upload, Transcribe, Translate ───────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser])
def transcribe_and_translate(request):
    """
    Accepts: audio file + target_language
    Returns: original transcript + translated text
    """
    audio_file      = request.FILES.get('audio')
    target_language = request.data.get('language', 'hi')  # Default: Hindi
 
    if not audio_file:
        return Response({'error': 'No audio file provided'}, status=400)
 
    # Save to DB first
    if request.user.is_authenticated:
        user = request.user
    else:
        user = User.objects.first()
    transcript_obj = AudioTranscript.objects.create(
        user       = user,
        audio_file = audio_file,
        target_language = target_language
    )
 
    # Get full path of saved file
    audio_path = os.path.join(settings.MEDIA_ROOT, str(transcript_obj.audio_file))
 
    # Step 1: Transcribe
    transcript = transcribe_audio(audio_path)
 
    # Step 2: Translate
    translated = translate_text(transcript, target_language)
 
    # Step 3: Save results
    transcript_obj.original_transcript = transcript
    transcript_obj.translated_text     = translated
    transcript_obj.save()
 
    return Response({
        'transcript':   transcript,
        'translation':  translated,
        'language':     target_language
    })
 
 
# ── Get all transcripts for logged-in user ────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_transcripts(request):
    transcripts = AudioTranscript.objects.filter(user=request.user)
    serializer  = AudioTranscriptSerializer(transcripts, many=True)
    return Response(serializer.data)
