from django.urls import path

from . import views


app_name='admin_panel'
urlpatterns = [
    path('add_account/', views.AddAccount.as_view(), name='add_account'),
    path('add_proxy/', views.AddProxy.as_view(), name='add_proxy'),
]