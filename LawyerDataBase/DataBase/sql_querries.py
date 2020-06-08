from .models import *
from django.db import connection
from datetime import date


def nom_value():
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT DISTINCT SUM(SE.nominal_value) AS nom '
            'FROM (( "Appointment_J_service" AS AJS INNER JOIN "Services" AS SE ON AJS.services_id = SE.service_code) '
            'INNER JOIN "Appointment_J" AS AJ ON AJS.appointment_j_id = AJ.appoint_code_j) '
            'WHERE AJ.code_dossier_j_id in '
            '(SELECT code_dossier_j FROM "Dossier_J" WHERE status=%s)', ['closed']
        )
        row1 = cursor.fetchone()[0]
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT DISTINCT SUM(SE.nominal_value) AS nom '
            'FROM (( "Appointment_N_service" AS ANS INNER JOIN "Services" AS SE ON ANS.services_id = SE.service_code) '
            'INNER JOIN "Appointment_N" AS AN ON ANS.appointment_n_id = AN.appoint_code_n) '
            'WHERE AN.code_dossier_n_id in '
            '(SELECT code_dossier_n FROM "Dossier_N" WHERE status=%s)', ['closed']
        )
        row2 = cursor.fetchone()[0]
    res = int(row1 or 0) + int(row2 or 0)
    return res

def extra_value():
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT DISTINCT SUM(SE.bonus_value) AS nom '
            'FROM (( "Appointment_J_service" AS AJS INNER JOIN "Services" AS SE ON AJS.services_id = SE.service_code) '
            'INNER JOIN "Appointment_J" AS AJ ON AJS.appointment_j_id = AJ.appoint_code_j) '
            'WHERE AJ.code_dossier_j_id in '
            '(SELECT code_dossier_j FROM "Dossier_J" WHERE status=%s)', ['closed-won']
        )
        row1 = cursor.fetchone()[0]
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT DISTINCT SUM(SE.bonus_value) AS nom '
            'FROM (( "Appointment_N_service" AS ANS INNER JOIN "Services" AS SE ON ANS.services_id = SE.service_code) '
            'INNER JOIN "Appointment_N" AS AN ON ANS.appointment_n_id = AN.appoint_code_n) '
            'WHERE AN.code_dossier_n_id in '
            '(SELECT code_dossier_n FROM "Dossier_N" WHERE status=%s)', ['closed-won']
        )
        row2 = cursor.fetchone()[0]
    res = int(row1 or 0) + int(row2 or 0)
    return res


def won_dossiers():
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT COUNT(*) '
            'FROM ((SELECT code_dossier_n FROM "Dossier_N" WHERE status=%s) '
            'UNION ALL '
            '(SELECT code_dossier_j FROM "Dossier_J" WHERE status=%s)) AS RES;', ['closed-won', 'closed-won'])
        row = cursor.fetchone()[0]
    return row


def lawyer_nom_value(param):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT DISTINCT res.lawyer_code AS la_code, SUM(res.nominal_value) AS nom '
            'FROM (SELECT LA.lawyer_code, SE.nominal_value '
            '       FROM ((( "Appointment_J_service" AS AJS INNER JOIN "Services" AS SE '
            '               ON AJS.services_id = SE.service_code) INNER JOIN "Appointment_J" AS AJ '
            '               ON AJS.appointment_j_id = AJ.appoint_code_j) INNER JOIN "Lawyer" AS LA '
            '               ON LA.lawyer_code = AJ.lawyer_code_id) '
            '           WHERE LA.lawyer_code = %s AND AJ.code_dossier_j_id in '
            '           (SELECT code_dossier_j '
            '           FROM "Dossier_J" '
            '           WHERE status=%s) '
            '       UNION '
            '       SELECT LA.lawyer_code, SE.nominal_value '
            '       FROM ((( "Appointment_N_service" AS AJS INNER JOIN "Services" AS SE '
            '           ON AJS.services_id = SE.service_code) INNER JOIN "Appointment_N" AS AJ '
            '           ON AJS.appointment_n_id = AJ.appoint_code_n) INNER JOIN "Lawyer" AS LA '
            '           ON LA.lawyer_code = AJ.lawyer_code_id) '
            '           WHERE LA.lawyer_code = %s AND AJ.code_dossier_n_id in '
            '           (SELECT code_dossier_j '
            '           FROM "Dossier_J" '
            '               WHERE status=%s)) AS res '
            'GROUP BY res.lawyer_code', [param, 'closed', param, 'closed'])
        row = cursor.fetchone()
    return row


def lawyer_extra_value(param):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT DISTINCT res.lawyer_code AS la_code, SUM(res.bonus_value) AS nom '
            'FROM (SELECT LA.lawyer_code, SE.bonus_value '
            '       FROM ((( "Appointment_J_service" AS AJS INNER JOIN "Services" AS SE '
            '               ON AJS.services_id = SE.service_code) INNER JOIN "Appointment_J" AS AJ '
            '               ON AJS.appointment_j_id = AJ.appoint_code_j) INNER JOIN "Lawyer" AS LA '
            '               ON LA.lawyer_code = AJ.lawyer_code_id) '
            '           WHERE LA.lawyer_code = %s AND AJ.code_dossier_j_id in '
            '           (SELECT code_dossier_j '
            '           FROM "Dossier_J" '
            '           WHERE status=%s) '
            '       UNION '
            '       SELECT LA.lawyer_code, SE.bonus_value '
            '       FROM ((( "Appointment_N_service" AS AJS INNER JOIN "Services" AS SE '
            '           ON AJS.services_id = SE.service_code) INNER JOIN "Appointment_N" AS AJ '
            '           ON AJS.appointment_n_id = AJ.appoint_code_n) INNER JOIN "Lawyer" AS LA '
            '           ON LA.lawyer_code = AJ.lawyer_code_id) '
            '           WHERE LA.lawyer_code = %s AND AJ.code_dossier_n_id in '
            '           (SELECT code_dossier_j '
            '           FROM "Dossier_J" '
            '               WHERE status=%s)) AS res '
            'GROUP BY res.lawyer_code', [param, 'closed-won', param, 'closed-won'])

        row = cursor.fetchone()
    return row


def service_counter():
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT service_code, name_service, nominal_value, bonus_value, status, COUNT(*) as counter '
            'FROM ( SELECT service_code, name_service, nominal_value, bonus_value, status '
            '       FROM((("Appointment_N" AS AN INNER JOIN "Appointment_N_service" AS ANS '
            '           ON AN.appoint_code_n = ANS.appointment_n_id) INNER JOIN "Services" AS SE'
            '           ON ANS.services_id = SE.service_code) INNER JOIN "Dossier_N" AS DN '
            '           ON DN.code_dossier_n = AN.code_dossier_n_id) '
            '   UNION ALL '
            '       SELECT service_code, name_service, nominal_value, bonus_value, status '
            '       FROM((("Appointment_J" AS AJ INNER JOIN "Appointment_J_service" AS AJS '
            '           ON AJ.appoint_code_j = AJS.appointment_j_id) INNER JOIN "Services" AS SE '
            '           ON AJS.services_id = SE.service_code) INNER JOIN "Dossier_J" AS DJ '
            '           ON DJ.code_dossier_j = AJ.code_dossier_j_id)) AS RES '
            'GROUP BY res.service_code, res.name_service, res.nominal_value, res.bonus_value, res.status')
        row = cursor.fetchall()
    res = []
    for record in row:
        # count sum, based on if dossier is closed
        sum = 0
        if record[4] == 'closed':
            sum = int(record[5])*int(record[2])
        elif record[4] =='closed-won':
            sum = int(record[5])*int(record[3])

        exists = False
        # if service is already added to array
        for service in res:
            if service['service_code'] == record[0]:
                exists = True
                service['sum'] = int(service['sum']) + sum
                service['count'] = int(service['count']) + int(record[5])
        # else
        if not exists:
            res.append({'service_code': record[0],
                        'name_service': record[1],
                        'count': record[5],
                        'nominal_value': record[2],
                        'bonus_value': record[3],
                        'sum':sum})
    return res


def lawyer_counter():
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT lawyer_code, first_name, surname, mid_name, COUNT(*), specialization, status, bonus_value, nominal_value '
            'FROM (( SELECT lawyer_code, first_name, surname, mid_name, specialization, status, bonus_value, nominal_value '
            '       FROM ((("Appointment_N" AS AN INNER JOIN "Lawyer" AS LA '
            '           ON AN.lawyer_code_id = LA.lawyer_code ) INNER JOIN "Appointment_N_service" AS ANS '
            '           ON ANS.appointment_n_id = AN.appoint_code_n) INNER JOIN "Services" AS SE '
            '           ON SE.service_code = ANS.services_id) INNER JOIN "Dossier_N" as DN '
            '           on DN.code_dossier_n = AN.code_dossier_n_id '
            '       ) '
            '   UNION ALL '
            '       ( SELECT lawyer_code, first_name, surname, mid_name, specialization, status, bonus_value, nominal_value '
            '            FROM ((("Appointment_J" AS AJ INNER JOIN "Lawyer" AS LA '
            '           ON AJ.lawyer_code_id = LA.lawyer_code ) INNER JOIN "Appointment_J_service" AS AJS '
            '           ON AJS.appointment_j_id = AJ.appoint_code_j) INNER JOIN "Services" AS SE '
            '           ON SE.service_code = AJS.services_id) INNER JOIN "Dossier_J" as DJ '
            '           on DJ.code_dossier_j = AJ.code_dossier_j_id '
            '       ) ) AS res '
            'GROUP BY res.lawyer_code, res.first_name, res.surname, res.mid_name, res.specialization,  '
            'res.status,  res.bonus_value,  res.nominal_value  ;')
        row = cursor.fetchall()
    res = []
    for record in row:
        sum = 0
        if record[6] == 'closed':
            sum = int(record[7]) * int(record[4])
        elif record[6] == 'closed-won':
            sum = int(record[8]) * int(record[4])

        exists = False
        for lawyer in res:
            if lawyer['lawyer_code'] == record[0]:
                exists = True
                lawyer['sum'] = int(lawyer['sum']) + sum
                lawyer['count'] = int(lawyer['count']) + int(record[4])

        if not exists:
            res.append({'lawyer_code': record[0],
                        'first_name': record[1],
                        'surname': record[2],
                        'count': record[4],
                        'mid_name': record[3],
                        'spec': record[5],
                        'sum': sum})
    return res


def date_closed_dossier_j(date1, date2):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT COUNT(*) AS counted_dossiers '
            'FROM "Dossier_J" '
            'WHERE status <> %s and date_closed > %s::date and date_closed < %s::date ',
            ['open',
             f'{date1.year}-{date1.month}-{date1.day}',
             f'{date2.year}-{date2.month}-{date2.day}'])
        row1 = cursor.fetchone()
    res = int(row1[0] or 0)
    return res


def date_closed_dossier_n(date1, date2):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT COUNT(*) AS counted_dossiers '
            'FROM "Dossier_N" '
            'WHERE status <> %s and date_closed > %s::date and date_closed < %s::date ',
            ['open',
             f'{date1.year}-{date1.month}-{date1.day}',
             f'{date2.year}-{date2.month}-{date2.day}'])
        row1 = cursor.fetchone()
    res = int(row1[0] or 0)
    return res


def date_open_dossier_n(date1, date2):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT COUNT(*) AS counted_dossiers '
            'FROM "Dossier_N" '
            'WHERE date_signed > %s::date and date_signed < %s::date ',
            [f'{date1.year}-{date1.month}-{date1.day}',
             f'{date2.year}-{date2.month}-{date2.day}'])
        row1 = cursor.fetchone()
    res = int(row1[0] or 0)
    return res


def date_open_dossier_j(date1, date2):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT COUNT(*) AS counted_dossiers '
            'FROM "Dossier_J" '
            'WHERE date_signed > %s::date and date_signed < %s::date ',
            [f'{date1.year}-{date1.month}-{date1.day}',
             f'{date2.year}-{date2.month}-{date2.day}'])
        row1 = cursor.fetchone()
    res = int(row1[0] or 0)
    return res


def date_service_counter(date1, date2):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT service_code, name_service, nominal_value, bonus_value, status, COUNT(*) as counter '
            'FROM ( SELECT service_code, name_service, nominal_value, bonus_value, status '
            '       FROM((("Appointment_N" AS AN INNER JOIN "Appointment_N_service" AS ANS '
            '           ON AN.appoint_code_n = ANS.appointment_n_id) INNER JOIN "Services" AS SE '
            '           ON ANS.services_id = SE.service_code) INNER JOIN "Dossier_N" AS DN '
            '           ON DN.code_dossier_n = AN.code_dossier_n_id) '
            '       WHERE app_date > %s::date and app_date < %s::date '
            '   UNION ALL '
            '       SELECT service_code, name_service, nominal_value, bonus_value, status '
            '       FROM((("Appointment_J" AS AJ INNER JOIN "Appointment_J_service" AS AJS '
            '           ON AJ.appoint_code_j = AJS.appointment_j_id) INNER JOIN "Services" AS SE '
            '           ON AJS.services_id = SE.service_code) INNER JOIN "Dossier_J" AS DJ '
            '           ON DJ.code_dossier_j = AJ.code_dossier_j_id) '
            '       WHERE app_date > %s::date and app_date < %s::date) AS RES '
            'GROUP BY res.service_code, res.name_service, res.nominal_value, res.bonus_value, res.status Order by res.service_code',
            [f'{date1.year}-{date1.month}-{date1.day}',
             f'{date2.year}-{date2.month}-{date2.day}',
             f'{date1.year}-{date1.month}-{date1.day}',
             f'{date2.year}-{date2.month}-{date2.day}'])
        row = cursor.fetchall()
    res = []
    for record in row:
        # count sum, based on if dossier is closed
        sum = 0
        if record[4] == 'closed':
            sum = int(record[5]) * int(record[2])
        elif record[4] == 'closed-won':
            sum = int(record[5]) * int(record[3])

        exists = False
        # if service is already added to array
        for service in res:
            if service['service_code'] == record[0]:
                exists = True
                service['sum'] = int(service['sum']) + sum
                service['count'] = int(service['count']) + int(record[5])
        # else
        if not exists:
            res.append({'service_code': record[0],
                        'name_service': record[1],
                        'count': record[5],
                        'nominal_value': record[2],
                        'bonus_value': record[3],
                        'sum': sum,
                        'fulltimeSum':0,
                        'fulltimeCount':0})

    date_fulltime_count(res)
    return res


def date_fulltime_count(arrayRes):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT service_code, nominal_value, bonus_value, status, COUNT(*) as counter '
            'FROM ( SELECT service_code, nominal_value, bonus_value, status '
            '       FROM((("Appointment_N" AS AN INNER JOIN "Appointment_N_service" AS ANS '
            '           ON AN.appoint_code_n = ANS.appointment_n_id) INNER JOIN "Services" AS SE'
            '           ON ANS.services_id = SE.service_code) INNER JOIN "Dossier_N" AS DN '
            '           ON DN.code_dossier_n = AN.code_dossier_n_id) '
            '   UNION ALL '
            '       SELECT service_code, nominal_value, bonus_value, status '
            '       FROM((("Appointment_J" AS AJ INNER JOIN "Appointment_J_service" AS AJS '
            '           ON AJ.appoint_code_j = AJS.appointment_j_id) INNER JOIN "Services" AS SE '
            '           ON AJS.services_id = SE.service_code) INNER JOIN "Dossier_J" AS DJ '
            '           ON DJ.code_dossier_j = AJ.code_dossier_j_id)) AS RES '
            'GROUP BY res.service_code, res.nominal_value, res.bonus_value, res.status')
        row = cursor.fetchall()

    for record in row:
        # count sum, based on if dossier is closed
        sum = 0
        if record[3] == 'closed':
            sum = int(record[4])*int(record[1])
        elif record[3] =='closed-won':
            sum = int(record[4])*int(record[2])

        for service in arrayRes:
            if service['service_code'] == record[0]:
                service['fulltimeSum'] = int(service['fulltimeSum']) + sum
                service['fulltimeCount'] = int(service['fulltimeCount']) + int(record[4])

    return arrayRes


def date_won_dossiers(date1, date2):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT COUNT(*) '
            'FROM ((SELECT code_dossier_n '
            '       FROM "Dossier_N" '
            '       WHERE status=%s and date_closed > %s::date and date_closed < %s::date ) '
            'UNION ALL '
            '       (SELECT code_dossier_j '
            '       FROM "Dossier_J" '
            '       WHERE status=%s and date_closed > %s::date and date_closed < %s::date )) AS RES;',
            ['closed-won',
             f'{date1.year}-{date1.month}-{date1.day}',
             f'{date2.year}-{date2.month}-{date2.day}',
             'closed-won',
             f'{date1.year}-{date1.month}-{date1.day}',
             f'{date2.year}-{date2.month}-{date2.day}'])
        row = cursor.fetchone()[0]
    return row

def date_lawyer_counter(date1, date2):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT lawyer_code, first_name, surname, mid_name, COUNT(*), specialization, status, bonus_value, nominal_value '
            'FROM (( SELECT lawyer_code, first_name, surname, mid_name, specialization, status, bonus_value, nominal_value '
            '       FROM ((("Appointment_N" AS AN INNER JOIN "Lawyer" AS LA '
            '           ON AN.lawyer_code_id = LA.lawyer_code ) INNER JOIN "Appointment_N_service" AS ANS '
            '           ON ANS.appointment_n_id = AN.appoint_code_n) INNER JOIN "Services" AS SE '
            '           ON SE.service_code = ANS.services_id) INNER JOIN "Dossier_N" as DN '
            '           on DN.code_dossier_n = AN.code_dossier_n_id '
            '       WHERE app_date > %s::date and app_date < %s::date ) '
            '   UNION ALL '
            '       ( SELECT lawyer_code, first_name, surname, mid_name, specialization, status, bonus_value, nominal_value '
        '            FROM ((("Appointment_J" AS AJ INNER JOIN "Lawyer" AS LA '
            '           ON AJ.lawyer_code_id = LA.lawyer_code ) INNER JOIN "Appointment_J_service" AS AJS '
            '           ON AJS.appointment_j_id = AJ.appoint_code_j) INNER JOIN "Services" AS SE '
            '           ON SE.service_code = AJS.services_id) INNER JOIN "Dossier_J" as DJ '
            '           on DJ.code_dossier_j = AJ.code_dossier_j_id '
            '       WHERE app_date > %s::date and app_date < %s::date ) ) AS res '
            'GROUP BY res.lawyer_code, res.first_name, res.surname, res.mid_name, res.specialization,  '
            'res.status,  res.bonus_value,  res.nominal_value  ;',
            [f'{date1.year}-{date1.month}-{date1.day}',
             f'{date2.year}-{date2.month}-{date2.day}',
             f'{date1.year}-{date1.month}-{date1.day}',
             f'{date2.year}-{date2.month}-{date2.day}'])
        row = cursor.fetchall()
    res = []
    for record in row:
        sum = 0
        if record[6] == 'closed':
            sum = int(record[7]) * int(record[4])
        elif record[6] == 'closed-won':
            sum = int(record[8]) * int(record[4])

        exists = False
        for lawyer in res:
            if lawyer['lawyer_code'] == record[0]:
                exists = True
                lawyer['sum'] = int(lawyer['sum']) + sum
                lawyer['count'] = int(lawyer['count']) + int(record[4])

        if not exists:
            res.append({'lawyer_code': record[0],
                        'first_name': record[1],
                        'surname': record[2],
                        'count': record[4],
                        'mid_name': record[3],
                        'spec': record[5],
                        'sum':sum})
    return res



def lawyers_appointment(services):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT la.lawyer_code, la.first_name, la.surname, la.mid_name, la.specialization '
            'FROM "Lawyer" la '
            'WHERE NOT EXISTS '
            '   ( SELECT * FROM "Lawyer_service" ls '
            '       WHERE services_id = ANY (%s)  '
            '       and la.lawyer_code not in '
            '               (select lawyer_id '
            '               from "Lawyer_service" '
            '               WHERE services_id = ls.services_id))',
            [services])
        row = cursor.fetchall()
    res = []
    for record in row:

        res.append({'lawyer_code': record[0],
                    'first_name': record[1],
                    'surname': record[2],
                    'mid_name': record[3],
                    'spec': record[4]})

    return res

def appoint_N_nom_value(param): #count appointment nominal value if Dossier = closed
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT AN.appoint_code_n, SUM(S.nominal_value) AS nom '
            'FROM (("Appointment_N" AS AN INNER JOIN "Appointment_N_service" AS ANS '
            'ON AN.appoint_code_n = ANS.appointment_n_id) INNER JOIN "Services" AS S '
            'ON ANS.services_id = S.service_code) INNER JOIN "Dossier_N" AS DN'
            'ON AN.code_dossier_n_id = DN.code_dossier_n'
            'WHERE AN.appoint_code_n = %s AND status=%s)'
            'GROUP BY AN.appoint_code_n;', [param, 'closed']
        )
        row = cursor.fetchone()
    return row


def appoint_N_extra_value(param): #count appointment bonus value if Dossier = closed-won
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT AN.appoint_code_n, SUM(S.bonus_value) AS extra '
            'FROM (("Appointment_N" AS AN INNER JOIN "Appointment_N_service" AS ANS '
            'ON AN.appoint_code_n = ANS.appointment_n_id) INNER JOIN "Services" AS S '
            'ON ANS.services_id = S.service_code) INNER JOIN "Dossier_N" AS DN '
            'ON AN.code_dossier_n_id = DN.code_dossier_n '
            'WHERE AN.appoint_code_n = %s AND status=%s '
            'GROUP BY AN.appoint_code_n;', [param, 'closed-won']
        )
        row = cursor.fetchone()
    return row


def appoint_J_nom_value(param): #count appointment nominal value if Dossier = closed
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT AJ.appoint_code_j, SUM(S.nominal_value) AS nom '
            'FROM (("Appointment_J" AS AJ INNER JOIN "Appointment_J_service" AS AJS '
            'ON AJ.appoint_code_j = AJS.appointment_j_id) INNER JOIN "Services" AS S '
            'ON AJS.services_id = S.service_code) INNER JOIN "Dossier_J" AS DJ '
            'ON AJ.code_dossier_j_id = DJ.code_dossier_j '
            'WHERE AJ.appoint_code_j = %s AND status=%s '
            'GROUP BY AJ.appoint_code_j; ', [param, 'closed']
        )
        row = cursor.fetchone()
    return row


def appoint_J_extra_value(param): #count appointment bonus value if Dossier = closed-won
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT AJ.appoint_code_j, SUM(S.bonus_value) AS extra '
            'FROM (("Appointment_J" AS AJ INNER JOIN "Appointment_J_service" AS AJS '
            'ON AJ.appoint_code_j = AJS.appointment_j_id) INNER JOIN "Services" AS S '
            'ON AJS.services_id = S.service_code) INNER JOIN "Dossier_J" AS DJ'
            'ON AJ.code_dossier_j_id = DJ.code_dossier_j'
            'WHERE AJ.appoint_code_j = %s AND status=%s '
            'GROUP BY AJ.appoint_code_j;', [param, 'closed-won']
        )
        row = cursor.fetchone()
    return row


def filter_lawyer_by_specialization(param):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT lawyer_code, first_name, surname, specialization, mail_info '
            'FROM "Lawyer"'
            'WHERE specialization = %s;', [param])
        row = cursor.fetchall()
    res = []
    for record in row:
        res.append({'lawyer_code': record[0],
                    'first_name': record[1],
                    'surname': record[2],
                    'mid_name': record[3],
                    'spec': record[4]})

    return res


def filter_dossier_n_by_status(param): #filter Dossier N by status
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT code_dossier_n, status, date_signed, date_expired, date_closed, fee, paid, num_client_n_id '
            'FROM "Dossier_N"'
            'WHERE status = %s;', [param])
        row = cursor.fetchall()
    res = []
    for record in row:
        res.append({'code_dossier_n': record[0],
                    'status': record[1],
                    'date_signed': record[2],
                    'date_expired': record[3],
                    'date_closed': record[4],
                    'fee': record[5],
                    'paid': record[6],
                    'num_client_n_id': record[7]})
    return res


def filter_dossier_j_by_status(param): #filter Dossier J by status
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT code_dossier_j, status, date_signed, date_expired, date_closed, fee, paid, num_client_j_id '
            'FROM "Dossier_J"'
            'WHERE status = %s;', [param])
        row = cursor.fetchall()
    res = []
    for record in row:
        res.append({'code_dossier_j': record[0],
                    'status': record[1],
                    'date_signed': record[2],
                    'date_expired': record[3],
                    'date_closed': record[4],
                    'fee': record[5],
                    'paid': record[6],
                    'num_client_j_id': record[7]})
    return res


#  get dates, which are chosen
def blocked_time_lawyer(lawyer,date):
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT to_char(RES.app_time, %s) '
            'FROM ( '
            '   (SELECT app_time '
        '        FROM "Appointment_J" AS AJ INNER JOIN "Lawyer" AS LA ON AJ.lawyer_code_id = LA.lawyer_code '
            '    WHERE AJ.app_date = %s::date AND LA.lawyer_code = %s ) '
            'UNION ALL '
            '   (SELECT app_time '
            '    FROM "Appointment_N" AS AN INNER JOIN "Lawyer" AS LA ON AN.lawyer_code_id = LA.lawyer_code '
            '    WHERE AN.app_date = %s::date AND LA.lawyer_code = %s )) AS RES;',
            ['HH24:MI',f'{date.year}-{date.month}-{date.day}',lawyer,
            f'{date.year}-{date.month}-{date.day}',lawyer])
        row = cursor.fetchall()
    res = []
    for record in row:
        res.append(record[0])
    return res

