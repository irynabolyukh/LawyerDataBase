from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.forms import ModelForm, inlineformset_factory, SelectDateWidget, SplitDateTimeWidget
from django import forms
from .models import *
from django.forms import Textarea, TimeInput, TextInput, CheckboxSelectMultiple



class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='Ім`я користувача', min_length=4, max_length=150)
    email = forms.EmailField(label='E-mail')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Підтвердіть пароль', widget=forms.PasswordInput)
    group = forms.ModelChoiceField(label='Група', queryset=Group.objects.all(), required=True)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError("Email already exists")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2


    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        user.groups.add(self.cleaned_data['group'])
        return user


class LawyerForm(ModelForm):
    lawyer_code = forms.CharField(label='Код свідоцтва', max_length=8, min_length=8)
    first_name = forms.CharField(label='Ім`я')
    surname = forms.CharField(label='Прізвище')
    mid_name = forms.CharField(label='По батькові')
    specialization = forms.CharField(label='Спеціалізація')
    mail_info = forms.EmailField(label='E-mail')
    service = forms.ModelMultipleChoiceField(label='Послуги', required=False,
                                             queryset=Services.objects.all(),
                                             widget=CheckboxSelectMultiple)
    work_days = forms.ModelMultipleChoiceField(label='Робочі дні', required=False,
                                             queryset=Work_days.objects.all(),
                                             widget=CheckboxSelectMultiple)

    class Meta:
        model = Lawyer
        fields = ['lawyer_code', 'first_name', 'surname',
                  'mid_name', 'specialization', 'mail_info', 'service', 'work_days']



LPhoneFormSet = inlineformset_factory(Lawyer, LPhone, max_num=2, fields=['phone_num'], labels={'phone_num': ('Телефон')})


class LawyerServiceForm(forms.Form):
    service_code = forms.CharField(label='Код послуги', disabled=True)
    lawyers = forms.ModelMultipleChoiceField(label='Адвокати', required=False,
                                             queryset=Lawyer.objects.all(),
                                             widget=CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super(LawyerServiceForm, self).__init__(*args, **kwargs)
        self.fields['service_code'].initial = pk
        # self.fields['lawyers'].queryset = Lawyer.objects.exclude(service=pk)


class ServiceGroupForm(ModelForm):
    name_group = forms.CharField(label='Назва групи', max_length=50)

    class Meta:
        model = ServiceGroup
        fields = '__all__'


class ServicesForm(ModelForm):
    service_code = forms.CharField(label='Код послуги', max_length=5, min_length=5)
    name_service = forms.CharField(label='Послуга', max_length=50)
    nominal_value = forms.DecimalField(label='Номінальна вартість', max_digits=6, decimal_places=2)
    bonus_value = forms.DecimalField(label='Бонусна вартість', max_digits=6, decimal_places=2)
    lawyers = forms.ModelMultipleChoiceField(label='Адвокати', required=False,
                                             queryset=Lawyer.objects.all(),
                                             widget=CheckboxSelectMultiple)
    service_group = forms.ModelChoiceField(label='Група послуг', required=False, queryset=ServiceGroup.objects.all())

    class Meta:
        model = Services
        fields = '__all__'


class ServicesUpdateForm(ModelForm):
    service_code = forms.CharField(label='Код послуги', max_length=5, min_length=5)
    name_service = forms.CharField(label='Послуга', max_length=50)
    nominal_value = forms.DecimalField(label='Номінальна вартість', max_digits=6, decimal_places=2)
    bonus_value = forms.DecimalField(label='Бонусна вартість', max_digits=6, decimal_places=2)
    service_group = forms.ModelChoiceField(label='Група послуг', queryset=ServiceGroup.objects.all())

    class Meta:
        model = Services
        fields = ['service_code', 'name_service', 'nominal_value',
                  'bonus_value', 'service_group']


NPhoneFormset = inlineformset_factory(Client_natural, NPhone, max_num=2, fields=['phone_num'], labels={'phone_num': ('Телефон')})

JPhoneFormset = inlineformset_factory(Client_juridical, JPhone, max_num=2, fields=['phone_num'], labels={'phone_num': ('Телефон')})


class Appointment_NForm(ModelForm):
    app_date = forms.DateField(label='Дата', widget=TextInput(attrs={'readonly': 'readonly'}))
    app_time = forms.TimeField(label='Час', widget=TimeInput(format='%H:%M'))
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(label='Послуги', queryset=Services.objects.all())
    num_client_n = forms.ModelChoiceField(label='Клієнт', queryset=Client_natural.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all())
    code_dossier_n = forms.ModelChoiceField(label='Досьє', queryset=Dossier_N.objects.all().filter(status='open'))

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
        if user.groups.filter(name="Фізичний клієнт").exists():
            user_id = Client_natural.objects.filter(mail_info=user.email)[0]
            self.fields['num_client_n'].initial=user_id.pk
            self.fields['num_client_n'].disabled = True
            self.fields['code_dossier_n'].queryset = Dossier_N.objects.filter(num_client_n=user_id).filter(status='open')


class Appointment_JForm(ModelForm):
    app_date = forms.DateField(label='Дата',widget=TextInput(attrs={'readonly':'readonly'}))
    app_time = forms.TimeField(label='Час',widget=TimeInput(format='%H:%M'))
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)
    service = forms.ModelMultipleChoiceField(label='Послуги', queryset=Services.objects.all())
    num_client_j = forms.ModelChoiceField(label='Клієнт', queryset=Client_juridical.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all())
    code_dossier_j = forms.ModelChoiceField(label='Досьє', queryset=Dossier_J.objects.all().filter(status='open'))

    class Meta:
        model = Appointment_J
        fields = ['num_client_j', 'code_dossier_j', 'service', 'lawyer_code', 'app_date', 'app_time', 'comment']


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(Appointment_JForm, self).__init__(*args, **kwargs)
        if user.groups.filter(name="Юридичний клієнт").exists():
            user_id = Client_juridical.objects.filter(mail_info=user.email)[0]
            self.fields['num_client_j'].initial=user_id.pk
            self.fields['num_client_j'].disabled = True
            self.fields['code_dossier_j'].queryset = Dossier_J.objects.filter(num_client_j=user_id).filter(status='open')


class Dossier_JForm(ModelForm):
    code_dossier_j = forms.CharField(label='Код', max_length=8, min_length=8)
    num_client_j = forms.ModelChoiceField(label='Клієнт', queryset=Client_juridical.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all(), required=False)
    issue = forms.CharField(label='Суть справи', widget=forms.Textarea)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_signed = forms.DateField(label='Дата підписання', widget=TextInput(attrs={'autocomplete':'off'}))
    date_expired = forms.DateField(label='Дата спливу', widget=TextInput(attrs={'autocomplete':'off'}))
    date_closed = forms.DateField(label='Дата закриття', required=False, widget=TextInput(attrs={'autocomplete':'off'}))
    fee = forms.DecimalField(label='Гонорар', initial=0)
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=100, label='Суд', required=False)
    court_adr = forms.CharField(max_length=300, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False, widget=TextInput(attrs={'autocomplete':'off'}))

    class Meta:
        model = Dossier_J
        fields = '__all__'


class Dossier_NForm(ModelForm):
    code_dossier_n = forms.CharField(label='Код', max_length=8, min_length=8)
    num_client_n = forms.ModelChoiceField(label='Клієнт', queryset=Client_natural.objects.all())
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all(), required=False)
    issue = forms.CharField(label='Суть справи', widget=forms.Textarea)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_signed = forms.DateField(label='Дата підписання', widget=TextInput(attrs={'autocomplete':'off'}))
    date_expired = forms.DateField(label='Дата спливу', widget=TextInput(attrs={'autocomplete':'off'}))
    date_closed = forms.DateField(label='Дата закриття', required=False, widget=TextInput(attrs={'autocomplete':'off'}))
    fee = forms.DecimalField(label='Гонорар', initial=0)
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=100, label='Суд', required=False)
    court_adr = forms.CharField(max_length=300, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False, widget=TextInput(attrs={'autocomplete':'off'}))

    def clean_paid(self):
        paidcontext = self.cleaned_data['paid']
        print(paidcontext)
        print(self.cleaned_data['status'])
        if paidcontext and str(self.cleaned_data['status']) == 'open':
            print("mem")
        return paidcontext

    def clean(self):
        cleaned_data = super(Dossier_NForm, self).clean()

        print(cleaned_data)
        return cleaned_data

    class Meta:
        model = Dossier_N
        fields = '__all__'


class Client_NForm(ModelForm):
    num_client_n = forms.CharField(label='Ідентифікаційний код', max_length=10, min_length=10)
    first_name = forms.CharField(label='Ім`я', max_length=50)
    surname = forms.CharField(label='Прізвище', max_length=50)
    mid_name = forms.CharField(label='По батькові', max_length=50)
    adr_city = forms.CharField(label='Місто', max_length=100)
    adr_street = forms.CharField(label='Вулиця', max_length=200)
    adr_build = forms.CharField(label='Будинок', max_length=5)
    mail_info = forms.EmailField(label='E-mail', max_length=30)
    birth_date = forms.DateField(label='Дата народження', widget=TextInput(attrs={'autocomplete':'off'}))
    passport_date = forms.DateField(label='Дата паспорта', widget=TextInput(attrs={'autocomplete':'off'}))
    passport_authority = forms.CharField(label='Орган паспорта', max_length=6, min_length=6)


    class Meta:
        model = Client_natural
        fields = '__all__'


class Client_JForm(ModelForm):
    num_client_j = forms.CharField(label='ЄДРПОУ', max_length=8, min_length=8)
    first_name = forms.CharField(label='Ім`я', max_length=50)
    surname = forms.CharField(label='Прізвище', max_length=50)
    mid_name = forms.CharField(label='По батькові', max_length=50)
    adr_city = forms.CharField(label='Місто', max_length=100)
    adr_street = forms.CharField(label='Вулиця', max_length=200)
    adr_build = forms.CharField(label='Будинок', max_length=5)
    mail_info = forms.EmailField(label='E-mail', max_length=30)
    client_position = forms.CharField(label='Посада', max_length=50)
    name_of_company = forms.CharField(label='Компанія', max_length=100)
    iban = forms.CharField(label='IBAN', max_length=29, min_length=29)

    class Meta:
        model = Client_juridical
        fields = '__all__'


class Appointment_NFormUpdate(ModelForm):
    app_date = forms.DateField(label='Дата',widget=TextInput(attrs={'autocomplete':'off'}))
    app_time = forms.TimeField(label='Час')
    comment = forms.CharField(label='Коментарій', required=False, widget=forms.Textarea)

    class Meta:
        model = Appointment_N
        fields = ['app_date', 'app_time', 'comment']
        widgets = {
            'app_time': TimeInput(format='%H:%M')
        }


class Appointment_JFormUpdate(ModelForm):
    app_date = forms.DateField(label='Дата', widget=TextInput(attrs={'autocomplete':'off'}))
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
    date_closed = forms.DateField(label='Дата закриття', required=False, widget=TextInput(attrs={'autocomplete':'off'}))
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=100, label='Суд', required=False)
    court_adr = forms.CharField(max_length=300, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False, widget=TextInput(attrs={'autocomplete':'off'}))

    class Meta:
        model = Dossier_J
        fields = ['date_closed', 'status', 'paid', 'court_name', 'court_adr', 'court_date', 'lawyer_code']


class Dossier_NFormUpdate(ModelForm):
    lawyer_code = forms.ModelChoiceField(label='Адвокат', queryset=Lawyer.objects.all(),
                                         required=False)
    status = forms.ChoiceField(label='Статус', choices=Dossier.DOS_STATUS)
    date_closed = forms.DateField(label='Дата закриття', required=False, widget=TextInput(attrs={'autocomplete':'off'}))
    paid = forms.BooleanField(label='Оплачено', required=False)
    court_name = forms.CharField(max_length=100, label='Суд', required=False)
    court_adr = forms.CharField(max_length=300, label='Адрес', required=False)
    court_date = forms.DateTimeField(label='Дата засідання', required=False, widget=TextInput(attrs={'autocomplete':'off'}))

    class Meta:
        model = Dossier_N
        fields = ['date_closed', 'status', 'paid', 'court_name', 'court_adr', 'court_date', 'lawyer_code']
