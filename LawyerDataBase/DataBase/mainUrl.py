from django.urls import path

from . import views

urlpatterns = [
    path('', views.visitCard, name='visitCard'),
]