from django.urls import path
from . import views

urlpatterns = [
    path('register/',                       views.register_view,   name='register'),
    path('login/',                          views.login_view,      name='login'),
    path('logout/',                         views.logout_view,     name='logout'),
    path('me/',                             views.me_view,         name='me'),
    path('profile/<str:username>/',         views.profile_view,    name='profile'),
    path('follow/<str:username>/',          views.follow_unfollow, name='follow'),
    path('search/',                         views.search_users,    name='search'),
    path('profile-page/<str:username>/',    views.profile_page,    name='profile_page'),
    path('change-password/',                views.change_password, name='change_password'),
]