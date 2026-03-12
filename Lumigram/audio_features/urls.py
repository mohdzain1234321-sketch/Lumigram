from django.urls import path
from . import views
 
urlpatterns = [
    path('transcribe/',   views.transcribe_and_translate, name='transcribe'),
    path('my-transcripts/', views.my_transcripts,         name='my-transcripts'),
]
