from django.db import models


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

    class Meta:
        db_table = 'Work_days'


class Services(models.Model):
    service_code = models.CharField(max_length=5, primary_key=True)
    name_service = models.CharField(max_length=50)
    nominal_value = models.DecimalField(max_digits=6, decimal_places=2)
    bonus_value = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = 'Services'



class Lawyer(models.Model):
    lawyer_code = models.CharField(max_length=8, primary_key=True)
    first_name = models.CharField(max_length=25)
    surname = models.CharField(max_length=25)
    mid_name = models.CharField(max_length=25)
    specialization = models.CharField(max_length=20)
    mail_info = models.EmailField(max_length=30)
    service = models.ManyToManyField(Services)
    work_days = models.ManyToManyField(Work_days)

    class Meta:
        db_table = 'Lawyer'
        ordering = ['first_name']

class LPhone(models.Model):
    phone_num = models.CharField(max_length=10)
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, related_name='phones')

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

class CPhone(models.Model):
    phone_num = models.CharField(max_length=10)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='phones')

    class Meta:
        db_table = 'CPhone'

class Client_natural(Client):
    num_client_n = models.CharField(max_length=10, primary_key=True)
    birth_date = models.DateField()
    passport_date = models.DateField()
    passport_authority = models.CharField(max_length=6)

    class Meta(Client.Meta):
        db_table = 'Client_natural'


class Client_juridical(Client):
    num_client_j = models.CharField(max_length=8, primary_key=True)
    clint_position = models.CharField(max_length=25)
    name_of_company = models.CharField(max_length=25)
    iban = models.CharField(max_length=29)

    class Meta(Client.Meta):
        db_table = 'Client_juridical'


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
    date_closed = models.DateField(blank=True)
    fee = models.DecimalField(max_digits=7, decimal_places=2)
    paid = models.BooleanField(default=False)
    court_name = models.CharField(max_length=50, blank=True)
    court_adr = models.CharField(max_length=50, blank=True)
    court_date = models.DateTimeField(null=True)
    lawyer_code = models.ForeignKey(Lawyer, on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True


class Dossier_N(Dossier):
    code_dossier_n = models.CharField(max_length=8, primary_key=True)
    num_client_n = models.ForeignKey(Client_natural, on_delete=models.DO_NOTHING)

    class Meta(Dossier.Meta):
        db_table = 'Dossier_N'


class Dossier_J(Dossier):
    code_dossier_j = models.CharField(max_length=8, primary_key=True)
    num_client_j = models.ForeignKey(Client_juridical, on_delete=models.DO_NOTHING)

    class Meta(Dossier.Meta):
        db_table = 'Dossier_J'


class Appointment(models.Model):
    app_date = models.DateField()
    app_time = models.TimeField()
    comment = models.TextField()
    service = models.ManyToManyField(Services)

    class Meta:
        abstract = True


class Appointment_N(Appointment):
    appoint_code_n = models.AutoField(primary_key=True)
    lawyer_code = models.ForeignKey(Lawyer, on_delete=models.DO_NOTHING)
    num_client_n = models.ForeignKey(Client_natural, on_delete=models.DO_NOTHING)
    code_dossier_n = models.ForeignKey(Dossier_N, on_delete=models.DO_NOTHING)

    class Meta(Appointment.Meta):
        db_table = 'Appointment_N'


class Appointment_J(Appointment):
    appoint_code_j = models.AutoField(primary_key=True)
    lawyer_code = models.ForeignKey(Lawyer, on_delete=models.DO_NOTHING)
    num_client_j = models.ForeignKey(Client_juridical, on_delete=models.DO_NOTHING)
    code_dossier_j = models.ForeignKey(Dossier_J, on_delete=models.DO_NOTHING)

    class Meta(Appointment.Meta):
        db_table = 'Appointment_J'
