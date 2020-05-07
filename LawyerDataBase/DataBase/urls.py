from django.urls import path

from . import views
from . import forms

urlpatterns = [
    path('', views.index, name='index'),
    path('lawyers/', views.lawyers, name='lawyers'),
    path('test/', views.test, name='test'),
    path('lawyer/<pk>/', views.LawyerDetailView.as_view(), name='lawyer-detailed-view'),
    path('lawyer/create', views.create_lawyer, name='lawyer-form'),
    path('client_natural/create', views.create_client_natural, name='client_natural-form'),
    path('client_juridical/create', views.create_client_juridical, name='client_juridical-form'),
    path('appointment_n/create', views.create_appointment_n, name='appointment_n-form'),
    path('appointment_j/create', views.create_appointment_j, name='appointment_j-form')

]
