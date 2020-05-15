from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# Create your models here.

class Work_days(models.Model):
    DAYS = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]
    day = models.CharField(max_length=3, choices=DAYS)

    def __str__(self):
        return f'{self.day}'

    class Meta:
        db_table = 'Work_days'
        ordering = ['id']


class Services(models.Model):
    service_code = models.CharField(max_length=5, primary_key=True)
    name_service = models.CharField(max_length=50)
    nominal_value = models.DecimalField(max_digits=6, decimal_places=2)
    bonus_value = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'{self.service_code} : {self.name_service}'

    class Meta:
        db_table = 'Services'

    def get_absolute_url(self):
        return reverse("service-detailed-view", kwargs={"pk": self.service_code})


class Lawyer(models.Model):
    lawyer_code = models.CharField(max_length=8, primary_key=True)
    first_name = models.CharField(max_length=25)
    surname = models.CharField(max_length=25)
    mid_name = models.CharField(max_length=25)
    specialization = models.CharField(max_length=20)
    mail_info = models.EmailField(max_length=30)
    service = models.ManyToManyField(Services)
    work_days = models.ManyToManyField(Work_days)

    def __str__(self):
        return f'{self.lawyer_code} : {self.first_name} {self.surname}'

    def getfullname(self):
        return f'{self.first_name} {self.surname} {self.mid_name}'

    class Meta:
        db_table = 'Lawyer'
        ordering = ['first_name']
        permissions = (
            ("view_statistics", "Can view statistics"),
            ("view_all_lawyers", "Can view all lawyers"),
            ("view_all_nclients", "Can view all nclients"),
            ("view_all_jclients", "Can view all jclients"),
            ("view_all_ndossiers", "Can view all ndossiers"),
            ("view_all_jdossiers", "Can view all jdossiers"),
        )

    def get_absolute_url(self):
        return reverse("lawyer-detailed-view", kwargs={"pk": self.lawyer_code})


class LPhone(models.Model):
    phone_num = models.CharField(max_length=10, primary_key=True)
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, related_name='phones')

    def __str__(self):
        return f'{self.phone_num} : {self.lawyer.lawyer_code}'

    class Meta:
        db_table = 'LPhone'


class Client(models.Model):
    first_name = models.CharField(max_length=25)
    surname = models.CharField(max_length=25)
    mid_name = models.CharField(max_length=25)
    adr_city = models.CharField(max_length=30)
    adr_street = models.CharField(max_length=20)
    adr_build = models.IntegerField()
    mail_info = models.EmailField(max_length=30)

    class Meta:
        abstract = True
        ordering = ['first_name']


class Client_natural(Client):
    num_client_n = models.CharField(max_length=10, primary_key=True)
    birth_date = models.DateField()
    passport_date = models.DateField()
    passport_authority = models.CharField(max_length=6)

    def __str__(self):
        return f'{self.num_client_n} : {self.first_name} {self.surname}'

    class Meta(Client.Meta):
        db_table = 'Client_natural'

    def getfullname(self):
        return f'{self.first_name} {self.surname} {self.mid_name}'

    def get_absolute_url(self):
        return reverse("client-detailed-view-n", kwargs={"pk": self.num_client_n})


class NPhone(models.Model):
    phone_num = models.CharField(max_length=10, primary_key=True)
    client_natural = models.ForeignKey(Client_natural, on_delete=models.CASCADE, related_name='phones')

    def __str__(self):
        return f'{self.phone_num} : {self.client_natural.num_client_n}'

    class Meta:
        db_table = 'NPhone'


class Client_juridical(Client):
    num_client_j = models.CharField(max_length=8, help_text='EDRPOU code', primary_key=True)
    client_position = models.CharField(max_length=25)
    name_of_company = models.CharField(max_length=25)
    iban = models.CharField(max_length=29)

    def __str__(self):
        return f'{self.num_client_j} : {self.first_name} {self.surname}'

    def getfullname(self):
        return f'{self.first_name} {self.surname} {self.mid_name}'

    class Meta(Client.Meta):
        db_table = 'Client_juridical'

    def get_absolute_url(self):
        return reverse("client-detailed-view-j", kwargs={"pk": self.num_client_j})


class JPhone(models.Model):
    phone_num = models.CharField(max_length=10, primary_key=True)
    client_juridical = models.ForeignKey(Client_juridical, on_delete=models.CASCADE, related_name='phones')

    def __str__(self):
        return f'{self.phone_num} : {self.client_juridical.num_client_j}'

    class Meta:
        db_table = 'JPhone'


class Dossier(models.Model):
    DOS_STATUS = [
        ('open', 'open'),
        ('closed', 'closed'),
        ('closed-won', 'closed-won'),
    ]
    issue = models.TextField()
    status = models.CharField(max_length=10, choices=DOS_STATUS, default='open')
    date_signed = models.DateField()
    date_expired = models.DateField()
    date_closed = models.DateField(blank=True, null=True)
    fee = models.DecimalField(max_digits=7, decimal_places=2)
    paid = models.BooleanField(default=False)
    court_name = models.CharField(max_length=50, blank=True, null=True)
    court_adr = models.CharField(max_length=50, blank=True, null=True)
    court_date = models.DateTimeField(blank=True, null=True)
    lawyer_code = models.ForeignKey(Lawyer, on_delete=models.DO_NOTHING,
                                    blank=True, null=True)

    class Meta:
        abstract = True


class Dossier_N(Dossier):
    code_dossier_n = models.CharField(max_length=8, primary_key=True)
    num_client_n = models.ForeignKey(Client_natural, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.code_dossier_n} : {self.num_client_n}'

    class Meta(Dossier.Meta):
        db_table = 'Dossier_N'

    def get_absolute_url(self):
        return reverse("dossier-detailed-n", kwargs={"pk": self.code_dossier_n})


class Dossier_J(Dossier):
    code_dossier_j = models.CharField(max_length=8, primary_key=True)
    num_client_j = models.ForeignKey(Client_juridical, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.code_dossier_j} : {self.num_client_j}'

    class Meta(Dossier.Meta):
        db_table = 'Dossier_J'

    def get_absolute_url(self):
        return reverse("dossier-detailed-j", kwargs={"pk": self.code_dossier_j})


class Appointment(models.Model):
    app_date = models.DateField()
    app_time = models.TimeField()
    comment = models.TextField(blank=True, null=True)
    service = models.ManyToManyField(Services)

    class Meta:
        abstract = True


class Appointment_N(Appointment):
    appoint_code_n = models.AutoField(primary_key=True)
    lawyer_code = models.ForeignKey(Lawyer, on_delete=models.DO_NOTHING)
    num_client_n = models.ForeignKey(Client_natural, on_delete=models.DO_NOTHING)
    code_dossier_n = models.ForeignKey(Dossier_N, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.appoint_code_n} : {self.num_client_n.getfullname()}'

    class Meta(Appointment.Meta):
        db_table = 'Appointment_N'


class Appointment_J(Appointment):
    appoint_code_j = models.AutoField(primary_key=True)
    lawyer_code = models.ForeignKey(Lawyer, on_delete=models.DO_NOTHING)
    num_client_j = models.ForeignKey(Client_juridical, on_delete=models.DO_NOTHING)
    code_dossier_j = models.ForeignKey(Dossier_J, on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.appoint_code_j} : {self.num_client_j.getfullname()}'

    class Meta(Appointment.Meta):
        db_table = 'Appointment_J'
        ordering = ['-app_date']
