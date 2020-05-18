from django.forms import ModelForm, inlineformset_factory
from django import forms
from .models import *


class LawyerForm(ModelForm):

    class Meta:
        model = Lawyer
        widgets = {
            'service': forms.CheckboxSelectMultiple,
            'work_days': forms.CheckboxSelectMultiple,
        }
        fields = ['lawyer_code', 'first_name', 'surname',
                  'mid_name', 'specialization', 'mail_info', 'service', 'work_days']


class LPhoneForm(ModelForm):
    class Meta:
        model = LPhone
        exclude = ()


LPhoneFormSet = inlineformset_factory(Lawyer, LPhone, fields=['phone_num'])


class ServicesForm(ModelForm):
    class Meta:
        model = Services
        fields = '__all__'


class ServicesForm(ModelForm):
    class Meta:
        model = Services
        fields = '__all__'


NPhoneFormset = inlineformset_factory(Client_natural, NPhone, max_num=3, fields=['phone_num'])

JPhoneFormset = inlineformset_factory(Client_juridical, JPhone, max_num=3, fields=['phone_num'])


class Appointment_NForm(ModelForm):
    comment = forms.CharField(required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(queryset=Services.objects.all())
    num_client_n = forms.ModelChoiceField(label='Client ID', queryset=Client_natural.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Lawyer code', queryset=Lawyer.objects.all())
    code_dossier_n = forms.ModelChoiceField(label='Dossier code', queryset=Dossier_N.objects.all())

    class Meta:
        model = Appointment_N
        fields = ['app_date', 'app_time', 'comment', 'service', 'num_client_n', 'lawyer_code', 'code_dossier_n']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        #self.fields['lawyer_code'].queryset = Lawyer.objects.none()

        # if 'service' in self.data:
        #     try:
        #         service_id = int(self.data.get('service'))
        #         self.fields['lawyer_code'].queryset = Lawyer.objects.all()
                    # .raw(
                    #         '''SELECT Lawyer.lawyer_code_id
                    #            FROM "Lawyer" x
                    #            WHERE service_id IN (SELECT service
                    #                                 FROM "Lawyer" y
                    #                                 WHERE x.lawyer_code_id = y.lawyer_code_id)''')
        #     except (ValueError, TypeError):
        #         pass  # invalid input from the client; ignore and fallback to empty Lawyer queryset
        # elif self.instance.pk:
        #     self.fields['lawyer_code'].queryset = self.instance.service.lawyer_set
    # def __init__(self, user, *args, **kwargs):
    #     super(Appointment_NForm, self).__init__(*args, **kwargs)
    #     self.fields['code_dossier_n'].queryset = Dossier_N.objects.filter(user=user)
    #     self.fields['num_client_n'].queryset = Client_natural.objects.filter(user=user)


class Appointment_JForm(ModelForm):
    comment = forms.CharField(required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(queryset=Services.objects.all())
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
