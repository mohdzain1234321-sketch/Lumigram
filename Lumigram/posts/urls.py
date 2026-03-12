from django.urls import path
from . import views

urlpatterns = [
    path('create/',                    views.create_post,    name='create-post'),
    path('feed/',                      views.feed,           name='feed'),
    path('all/',                       views.all_posts,      name='all-posts'),
    path('<int:post_id>/like/',        views.like_post,      name='like-post'),
    path('<int:post_id>/comment/',     views.add_comment,    name='add-comment'),
    path('<int:post_id>/comments/',    views.get_comments,   name='get-comments'),
    path('<int:post_id>/analytics/',   views.post_analytics, name='post-analytics'),
    path('<int:post_id>/detail/',      views.post_detail,    name='post-detail'),
]