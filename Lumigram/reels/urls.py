# reels/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                       views.list_reels,    name='list_reels'),
    path('create/',                views.create_reel,   name='create_reel'),
    path('<int:reel_id>/like/',    views.like_reel,     name='like_reel'),
    path('<int:reel_id>/comment/', views.comment_reel,  name='comment_reel'),
    path('user/<str:username>/',   views.user_reels,    name='user-reels'),  # ← ADD THIS
]