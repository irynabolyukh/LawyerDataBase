from django.urls import path

from . import views
from . import forms

urlpatterns = [
    path('', views.index, name='index'),
    path('lawyers/', views.lawyers, name='lawyers'),
    path('test/', views.test, name='test'),
    path('lawyer/<pk>/', views.LawyerDetailView.as_view(), name='lawyer-detailed-view'),
    path('service/<pk>/', views.ServiceDetailView.as_view(), name='service-detailed-view'),
    path('client_N/<pk>/', views.ClientNDetailView.as_view(), name='client-detailed-view-n'),
    path('client_J/<pk>/', views.ClientJDetailView.as_view(), name='client-detailed-view-j'),
    path('dossier_N/<pk>/', views.DossierDetailNView.as_view(), name='dossier-detailed-n'),
    path('dossier_J/<pk>/', views.DossierDetailJView.as_view(), name='dossier-detailed-j'),
    path('lawyer/create',views.create_lawyer, name='lawyer-form')
]
