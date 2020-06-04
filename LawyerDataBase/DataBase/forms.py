from django.forms import ModelForm, inlineformset_factory
from django import forms
from .models import *
from django.forms import TimeInput


class LawyerForm(ModelForm):
    lawyer_code = forms.CharField(label='Код свідоцтва')
    first_name = forms.CharField(label='Ім`я')
    surname = forms.CharField(label='Прізвище')
    mid_name = forms.CharField(label='По батькові')
    specialization = forms.CharField(label='Спеціалізація')
    mail_info = forms.EmailField(label='E-mail')

    class Meta:
        model = Lawyer
        widgets = {
            'service': forms.CheckboxSelectMultiple,
            'work_days': forms.CheckboxSelectMultiple
        }
        fields = ['lawyer_code', 'first_name', 'surname',
                  'mid_name', 'specialization', 'mail_info', 'service', 'work_days']


class LPhoneForm(ModelForm):
    class Meta:
        model = LPhone
        exclude = ()


LPhoneFormSet = inlineformset_factory(Lawyer, LPhone, max_num=2, fields=['phone_num'])


class ServicesForm(ModelForm):
    service_code = forms.CharField(label='Код послуги')
    name_service = forms.CharField(label='Послуга')
    nominal_value = forms.DecimalField(label='Номінальна вартість')
    bonus_value = forms.DecimalField(label='Бонусна вартість')

    class Meta:
        model = Services
        fields = '__all__'


NPhoneFormset = inlineformset_factory(Client_natural, NPhone, max_num=2, fields=['phone_num'])

JPhoneFormset = inlineformset_factory(Client_juridical, JPhone, max_num=2, fields=['phone_num'])


class Appointment_NForm(ModelForm):
    app_date = forms.DateField(label='Дата')
    app_time = forms.TimeField(label='Час')
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(label='Послуги', queryset=Services.objects.all())
    num_client_n = forms.ModelChoiceField(label='Клієнт', queryset=Client_natural.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all())
    code_dossier_n = forms.ModelChoiceField(label='Досьє', queryset=Dossier_N.objects.all())

    class Meta:
        model = Appointment_N
        fields = ['app_date', 'app_time', 'comment', 'service', 'num_client_n', 'lawyer_code', 'code_dossier_n']
        widgets = {
            'app_time': TimeInput(format='%H:%M')
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
    app_date = forms.DateField(label='Дата')
    app_time = forms.TimeField(label='Час')
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(label='Послуги', queryset=Services.objects.all())
    num_client_j = forms.ModelChoiceField(label='Клієнт', queryset=Client_juridical.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all())
    code_dossier_j = forms.ModelChoiceField(label='Досьє', queryset=Dossier_J.objects.all())

    class Meta:
        model = Appointment_J
        fields = ['app_date', 'app_time', 'comment', 'service', 'num_client_j', 'lawyer_code', 'code_dossier_j']
        widgets = {
            'app_time': TimeInput(format='%H:%M')
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(Appointment_JForm, self).__init__(*args, **kwargs)
        if user.groups.filter(name="ClientsJ").exists():
            user_id = Client_juridical.objects.filter(mail_info=user.email)[0]
            self.fields['num_client_j'].initial=user_id.pk
            self.fields['num_client_j'].disabled = True
            self.fields['code_dossier_j'].queryset = Dossier_J.objects.filter(num_client_j=user_id)


class Dossier_JForm(ModelForm):
    code_dossier_j = forms.CharField(label='Код', max_length=8)
    num_client_j = forms.ModelChoiceField(label='Клієнт', queryset=Client_juridical.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all(), required=False)
    issue = forms.CharField(label='Суть справи', widget=forms.Textarea)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_signed = forms.DateField(label='Дата підписання')
    date_expired = forms.DateField(label='Дата спливу')
    date_closed = forms.DateField(label='Дата закриття', required=False)
    fee = forms.DecimalField(label='Гонорар')
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=50, label='Суд', required=False)
    court_adr = forms.CharField(max_length=50, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False)

    class Meta:
        model = Dossier_J
        fields = '__all__'


class Dossier_NForm(ModelForm):
    code_dossier_n = forms.CharField(label='Код', max_length=8)
    num_client_n = forms.ModelChoiceField(label='Клієнт', queryset=Client_juridical.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all(), required=False)
    issue = forms.CharField(label='Суть справи', widget=forms.Textarea)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_signed = forms.DateField(label='Дата підписання')
    date_expired = forms.DateField(label='Дата спливу')
    date_closed = forms.DateField(label='Дата закриття', required=False)
    fee = forms.DecimalField(label='Гонорар')
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=50, label='Суд', required=False)
    court_adr = forms.CharField(max_length=50, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False)

    class Meta:
        model = Dossier_N
        fields = '__all__'


class Client_NForm(ModelForm):
    num_client_n = forms.CharField(label='Ідентифікаційний код', max_length=10)
    first_name = forms.CharField(label='Ім`я', max_length=25)
    surname = forms.CharField(label='Прізвище', max_length=25)
    mid_name = forms.CharField(label='По батькові', max_length=25)
    adr_city = forms.CharField(label='Місто', max_length=30)
    adr_street = forms.CharField(label='Вулиця', max_length=20)
    adr_build = forms.IntegerField(label='Будинок')
    mail_info = forms.EmailField(label='E-mail', max_length=30)
    birth_date = forms.DateField(label='Дата народження')
    passport_date = forms.DateField(label='Дата паспорта')
    passport_authority = forms.CharField(label='Орган паспорта', max_length=6)

    class Meta:
        model = Client_natural
        fields = '__all__'


class Client_JForm(ModelForm):
    num_client_j = forms.CharField(label='ЄДРПОУ', max_length=8)
    first_name = forms.CharField(label='Ім`я', max_length=25)
    surname = forms.CharField(label='Прізвище', max_length=25)
    mid_name = forms.CharField(label='По батькові', max_length=25)
    adr_city = forms.CharField(label='Місто', max_length=30)
    adr_street = forms.CharField(label='Вулиця', max_length=20)
    adr_build = forms.IntegerField(label='Будинок')
    mail_info = forms.EmailField(label='E-mail', max_length=30)
    client_position = forms.CharField(label='Посада', max_length=25)
    name_of_company = forms.CharField(label='Компанія', max_length=25)
    iban = forms.CharField(label='IBAN', max_length=29)

    class Meta:
        model = Client_juridical
        fields = '__all__'


class Appointment_NFormUpdate(ModelForm):
    app_date = forms.DateField(label='Дата')
    app_time = forms.TimeField(label='Час')
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)

    class Meta:
        model = Appointment_N
        fields = ['app_date', 'app_time', 'comment']
        widgets = {
            'app_time': TimeInput(format='%H:%M')
        }


class Appointment_JFormUpdate(ModelForm):
    app_date = forms.DateField(label='Дата')
    app_time = forms.TimeField(label='Час')
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)

    class Meta:
        model = Appointment_J
        fields = ['app_date', 'app_time', 'comment']
        widgets = {
            'app_time': TimeInput(format='%H:%M')
        }


class Dossier_JFormUpdate(ModelForm):
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all(), required=False)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_closed = forms.DateField(label='Дата закриття', required=False)
    fee = forms.DecimalField(label='Гонорар')
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=50, label='Суд', required=False)
    court_adr = forms.CharField(max_length=50, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False)

    class Meta:
        model = Dossier_J
        fields = ['date_closed', 'status', 'paid', 'fee', 'court_name', 'court_adr', 'court_date', 'lawyer_code']


class Dossier_NFormUpdate(ModelForm):
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all(), required=False)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_closed = forms.DateField(label='Дата закриття', required=False)
    fee = forms.DecimalField(label='Гонорар')
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=50, label='Суд', required=False)
    court_adr = forms.CharField(max_length=50, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False)

    class Meta:
        model = Dossier_N
        fields = ['date_closed', 'status', 'paid', 'fee', 'court_name', 'court_adr', 'court_date', 'lawyer_code']
