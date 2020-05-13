from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.sqltest, name='sqltest'),
    path('lawyers/', views.lawyers, name='lawyers'),
    path('ncustomers/', views.ncustomers, name='ncustomers'),
    path('jcustomers/', views.jcustomers, name='jcustomers'),
    path('ndossiers/', views.ndossiers, name='ndossiers'),
    path('jdossiers/', views.jdossiers, name='jdossiers'),
    path('lawyer/<pk>/', views.LawyerDetailView.as_view(), name='lawyer-detailed-view'),
    path('lawyer/create', views.LawyerCreateView.as_view(), name='lawyer-form'),
    path('lawyer/<pk>/update', views.LawyerUpdateView.as_view(), name='lawyer-update'),
    path('lawyer/<pk>/delete', views.LawyerDeleteView.as_view(), name='lawyer-delete'),
    path('client_N/create', views.Client_naturalCreateView.as_view(), name='client_natural-form'),
    path('client_N/<pk>/update', views.Client_naturalUpdateView.as_view(), name='client_natural-update'),
    path('client_N/<pk>/delete', views.Client_naturalDeleteView.as_view(), name='client_natural-delete'),
    path('client_J/create', views.Client_juridicalCreateView.as_view(), name='client_juridical-form'),
    path('client_J/<pk>/update', views.Client_juridicalUpdateView.as_view(), name='client_juridical-update'),
    path('client_J/<pk>/delete', views.Client_juridicalDeleteView.as_view(), name='client_juridical-delete'),
    path('appointment_N/create', views.create_appointment_n, name='appointment_n-form'),
    path('appointment_J/create', views.create_appointment_j, name='appointment_j-form'),
    path('service/create', views.ServicesCreateView.as_view(), name='service-create'),
    path('service/<pk>/update', views.ServicesUpdateView.as_view(), name='service-update'),
    path('service/<pk>/delete', views.ServicesDeleteView.as_view(), name='service-delete'),
    path('dossier_N/create', views.create_dossier_n, name='dossier_n-form'),
    path('dossier_J/create', views.create_dossier_j, name='dossier_j-form'),
    path('service/<pk>/', views.ServiceDetailView.as_view(), name='service-detailed-view'),
    path('client_N/<pk>/', views.ClientNDetailView.as_view(), name='client-detailed-view-n'),
    path('client_J/<pk>/', views.ClientJDetailView.as_view(), name='client-detailed-view-j'),
    path('dossier_N/<pk>/', views.DossierDetailNView.as_view(), name='dossier-detailed-n'),
    path('dossier_J/<pk>/', views.DossierDetailJView.as_view(), name='dossier-detailed-j')
]
