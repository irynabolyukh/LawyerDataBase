from django.forms import ModelForm, inlineformset_factory
from django import forms
from .models import *
from django.forms import Textarea, TimeInput, TextInput


class LawyerForm(ModelForm):
    lawyer_code = forms.CharField(label='Код свідоцтва')
    first_name = forms.CharField(label='Імя')
    surname = forms.CharField(label='Прізвище')
    mid_name = forms.CharField(label='По батькові')
    specialization = forms.CharField(label='Спеціалізація')
    mail_info = forms.EmailField(label='E-mail')

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
    service_code = forms.CharField(label='Код послуги')
    name_service = forms.CharField(label='Послуга')
    nominal_value = forms.DecimalField(label='Номінальна вартість')
    bonus_value = forms.DecimalField(label='Бонусна вартість')

    class Meta:
        model = Services
        fields = '__all__'


NPhoneFormset = inlineformset_factory(Client_natural, NPhone, max_num=3, fields=['phone_num'])

JPhoneFormset = inlineformset_factory(Client_juridical, JPhone, max_num=3, fields=['phone_num'])


class Appointment_NForm(ModelForm):
    app_date = forms.DateField(label='Дата', widget=TextInput(attrs={'readonly': 'readonly'}))
    app_time = forms.TimeField(label='Час', widget=TimeInput(format='%H:%M'))
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(label='Послуги', queryset=Services.objects.all())
    num_client_n = forms.ModelChoiceField(label='Клієнт', queryset=Client_natural.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all())
    code_dossier_n = forms.ModelChoiceField(label='Досьє', queryset=Dossier_N.objects.all())

    class Meta:
        model = Appointment_N
        fields = ['num_client_n','code_dossier_n','service', 'lawyer_code', 'app_date', 'app_time', 'comment']
        widgets = {
            'app_time': TimeInput(format='%H:%M'),
            'app_date': TextInput(attrs={'readonly': 'readonly'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(Appointment_NForm, self).__init__(*args, **kwargs)
        if user.groups.filter(name="ClientsN").exists():
            user_id = Client_natural.objects.filter(mail_info=user.email)[0]
            self.fields['num_client_n'].initial=user_id.pk
            self.fields['num_client_n'].disabled = True
            self.fields['code_dossier_n'].queryset = Dossier_N.objects.filter(num_client_n=user_id)

class Appointment_JForm(ModelForm):
    app_date = forms.DateField(label='Дата',widget=TextInput(attrs={'readonly':'readonly'}))
    app_time = forms.TimeField(label='Час',widget=TimeInput(format='%H:%M'))
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(label='Послуги', queryset=Services.objects.all())
    num_client_j = forms.ModelChoiceField(label='Клієнт', queryset=Client_juridical.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all())
    code_dossier_j = forms.ModelChoiceField(label='Досьє', queryset=Dossier_J.objects.all())

    class Meta:
        model = Appointment_J
        fields = ['num_client_j','code_dossier_j', 'service', 'lawyer_code', 'app_date', 'app_time', 'comment']


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(Appointment_JForm, self).__init__(*args, **kwargs)
        if user.groups.filter(name="ClientsJ").exists():
            user_id = Client_juridical.objects.filter(mail_info=user.email)[0]
            self.fields['num_client_j'].initial=user_id.pk
            self.fields['num_client_j'].disabled = True
            self.fields['code_dossier_j'].queryset = Dossier_J.objects.filter(num_client_j=user_id)


class Dossier_JForm(ModelForm):
    class Meta:
        model = Dossier_J
        fields = '__all__'


class Dossier_NForm(ModelForm):
    class Meta:
        model = Dossier_N
        fields = '__all__'
