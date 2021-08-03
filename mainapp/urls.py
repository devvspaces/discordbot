from django.urls import path

from . import views


app_name='dashboard'
urlpatterns = [
    path('dashboard/', views.Dashboard.as_view(), name='home'),
    path('packages/', views.Packages.as_view(), name='packages'),
    path('support/', views.Support.as_view(), name='support'),
    path('faq/', views.Faq.as_view(), name='faq'),
    path('dmpanel/', views.DmPanel.as_view(), name='dm_panel'),
]