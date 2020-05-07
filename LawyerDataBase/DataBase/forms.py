from django.forms import ModelForm
from django import forms
from .models import *


class LawyerForm(ModelForm):
    service = forms.ModelMultipleChoiceField(queryset=Services.objects.all(), widget=forms.CheckboxSelectMultiple)
    work_days = forms.ModelMultipleChoiceField(queryset=Work_days.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Lawyer
        fields = ['lawyer_code', 'first_name', 'surname',
                  'mid_name', 'specialization', 'mail_info', 'service', 'work_days']


class ServicesForm(ModelForm):
    class Meta:
        model = Services
        fields = '__all__'


class Client_naturalForm(ModelForm):
    class Meta:
        model = Client_natural
        fields = ['num_client_n', 'first_name', 'surname', 'mid_name',
                  'mail_info', 'adr_city', 'adr_street', 'adr_build',
                  'birth_date', 'passport_date', 'passport_authority']


class Client_juridicalForm(ModelForm):
    class Meta:
        model = Client_juridical
        fields = ['num_client_j', 'first_name', 'surname', 'mid_name',
                  'mail_info', 'client_position', 'name_of_company', 'iban',
                  'adr_city', 'adr_street', 'adr_build']


class Appointment_NForm(ModelForm):
    comment = forms.CharField(required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(queryset=Services.objects.all(), widget=forms.CheckboxSelectMultiple)
    num_client_n = forms.ModelChoiceField(label='Client ID', queryset=Client_natural.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Lawyer code', queryset=Lawyer.objects.all())
    code_dossier_n = forms.ModelChoiceField(label='Dossier code', queryset=Dossier_N.objects.all())
    class Meta:
        model = Appointment_N
        fields = ['app_date', 'app_time', 'comment', 'service', 'num_client_n', 'lawyer_code', 'code_dossier_n']


class Appointment_JForm(ModelForm):
    comment = forms.CharField(required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(queryset=Services.objects.all(), widget=forms.CheckboxSelectMultiple)
    num_client_j = forms.ModelChoiceField(label='Client ID', queryset=Client_juridical.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Lawyer code', queryset=Lawyer.objects.all())
    code_dossier_j = forms.ModelChoiceField(label='Dossier code', queryset=Dossier_J.objects.all())
    class Meta:
        model = Appointment_J
        fields = ['app_date', 'app_time', 'comment', 'service', 'num_client_j', 'lawyer_code', 'code_dossier_j']


class Dossier_JForm(ModelForm):
    class Meta:
        model = Dossier_J
        fields = '__all__'


class Dossier_NForm(ModelForm):
    class Meta:
        model = Dossier_N
        fields = '__all__'
