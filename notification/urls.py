from django.urls import path

from . import views


app_name='notification'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('webchat/<room_name>/', views.chat, name='chat'),
]