from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('lawyers/', views.lawyers, name='lawyers'),
    path('test/', views.test, name='test'),
]