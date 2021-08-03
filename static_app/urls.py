from django.urls import path

from . import views


app_name='basic'
urlpatterns = [
    path('', views.Landing.as_view(), name='landing_page'),
    path('pricing/', views.Pricing.as_view(), name='pricing'),
]
