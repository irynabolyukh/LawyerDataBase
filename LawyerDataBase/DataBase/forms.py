from django.forms import ModelForm
from django import forms
from .models import *


class LawyerForm(ModelForm):
    class Meta:
        model = Lawyer
        fields = ['lawyer_code', 'first_name', 'surname',
                  'mid_name', 'specialization', 'mail_info', 'service', 'work_days']


class ServicesForm(ModelForm):
    class Meta:
        model = Services
        fields = ['service_code', 'name_service', 'nominal_value', 'bonus_value']
