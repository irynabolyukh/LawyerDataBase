from django.urls import path

from . import views
from . import forms

urlpatterns = [
    path('', views.index, name='index'),
    path('lawyers/', views.lawyers, name='lawyers'),
    path('test/', views.test, name='test'),
    path('lawyer/<pk>/', views.LawyerDetailView.as_view(), name='lawyer-detailed-view'),
    path('lawyer/create', views.create_lawyer, name='lawyer-form'),
    path('client_N/create', views.create_client_natural, name='client_natural-form'),
    path('client_J/create', views.create_client_juridical, name='client_juridical-form'),
    path('appointment_N/create', views.create_appointment_n, name='appointment_n-form'),
    path('appointment_J/create', views.create_appointment_j, name='appointment_j-form'),
    path('service/<pk>/', views.LawyerDetailView.as_view(), name='service-detailed-view'),
    path('client_N/<pk>/', views.ClientNDetailView.as_view(), name='client-detailed-view-n'),
    path('client_J/<pk>/', views.LawyerDetailView.as_view(), name='client-detailed-view-j'),
    path('dossier_N/<pk>/', views.DossierDetailNView.as_view(), name='dossier-detailed-n'),
    path('dossier_J/<pk>/', views.DossierDetailJView.as_view(), name='dossier-detailed-j')
]
