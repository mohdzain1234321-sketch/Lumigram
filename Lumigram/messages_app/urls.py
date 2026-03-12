from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_conversations, name='conversations'),
    path('start/', views.get_or_create_conversation, name='start_conversation'),
    path('<int:convo_id>/messages/', views.get_messages, name='get_messages'),
    path('<int:convo_id>/send/', views.send_message, name='send_message'),
    path('share-post/', views.share_post, name='share_post'),
]