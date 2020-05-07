from django.urls import path

from . import views
from . import forms

urlpatterns = [
    path('', views.index, name='index'),
    path('lawyers/', views.lawyers, name='lawyers'),
    path('test/', views.test, name='test'),
    path('lawyer/<pk>/', views.LawyerDetailView.as_view(), name='lawyer-detailed-view'),
    path('service/<pk>/', views.LawyerDetailView.as_view(), name='lawyer-detailed-view'),
    path('client/<pk>/', views.LawyerDetailView.as_view(), name='lawyer-detailed-view'),
    path('dossier/<pk>/', views.DossierDetailJView.as_view(), name='lawyer-detailed-view'),
    path('dossier/<pk>/', views.DossierDetailNView.as_view(), name='lawyer-detailed-view'),
    path('lawyer/create',views.create_lawyer, name='lawyer-form')
]
