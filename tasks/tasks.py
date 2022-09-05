from celery import Celery
from django.apps import apps
from django.conf import settings

from django.db import connection
from django.utils import timezone
import requests

from requests import ReadTimeout, ConnectTimeout, ConnectionError, HTTPError


app = Celery()

status_codes = {
    'created': 1,
    'sent': 2,
    'canceled': 3,
    'error': 4
}


def schedule_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, get_clients_list.s())


def time_to_send(date_start, date_stop):
    if date_start < timezone.now() < date_stop:
        return True
    else:
        return False


@app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, max_retries=None)
def send_mailing(self, client_id, mail_list_id):
    from client.models import Client
    from mailing_list.models import MailingList, Message
    msg = Message.objects.filter(client_id=client_id, mailing_list_id=mail_list_id).first()
    client = Client.objects.get(id=client_id)
    m_list = MailingList.objects.get(id=mail_list_id)
    if not client or not client.is_active or not m_list or not m_list.is_active or not time_to_send(
            m_list.start_mailing, m_list.stop_mailing):
        if msg:
            if m_list.stop_mailing < timezone.now():
                msg.status_id = status_codes['canceled']
                msg.save()
                return
            elif m_list.start_mailing > timezone.now():
                msg.delete()
                return
    elif not msg:
        msg = Message.objects.create(client_id=client, mailing_list_id=m_list, status_id=1)
    elif msg.status_id == status_codes['sent'] or msg.status_id == status_codes['canceled']:
        return
    message_data = {'id': msg.id, 'phone': client.phone, 'text': m_list.message_text}
    url = f'{settings.MESSAGE_GATEWAY_URL}v1/send/{msg.id}'
    token = settings.AUTH_TOKEN
    headers = {
        'Authorization': 'Bearer ' + token
    }
    try:
        response = requests.post(url=url, json=message_data, headers=headers)
    except (ReadTimeout, ConnectTimeout, ConnectionError, HTTPError) as err:
        msg.status_id = status_codes['error']
        msg.save()
        raise Exception('Connection problems')
    else:
        response_data = response.json()
        if 'code' in response_data and response_data['code'] == 0:
            msg.status_id = status_codes['sent']
            msg.save()
        else:
            print(response_data)
            msg.status_id = status_codes['error']
            msg.save()
            raise Exception('Server response with error')


@app.task(bind=True)
def get_clients_list(self):
    if not apps.ready:
        return

    with connection.cursor() as cursor:
        sqlquery = "SELECT DISTINCT client_client.id, mailing_list_mailinglist.id " \
                   "FROM client_client LEFT OUTER JOIN client_clienttag ON client_client.id = " \
                   "client_clienttag.client_id_id " \
                   "LEFT JOIN mailing_list_message AS mm1 ON mm1.client_id_id = client_client.id " \
                   "CROSS JOIN mailing_list_mailinglist LEFT OUTER JOIN mailing_list_message AS mm2 " \
                   "ON mm2.mailing_list_id_id = mailing_list_mailinglist.id " \
                   "WHERE mailing_list_mailinglist.is_active = true AND client_client.is_active = true " \
                   "AND (mm1.id IS NULL OR mm2.id IS NULL) AND mailing_list_mailinglist.start_mailing < NOW() AND " \
                   "NOW() < mailing_list_mailinglist.stop_mailing AND " \
                   "(mailing_list_mailinglist.code = client_client.code OR " \
                   "mailing_list_mailinglist.tag = client_clienttag.tag)"
        cursor.execute(sqlquery)
        rows = cursor.fetchall()
        for r in rows:
            send_mailing.delay(r[0], r[1])
