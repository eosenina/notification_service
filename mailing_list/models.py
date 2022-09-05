from django.db import models
from client.models import Client


class MailingList(models.Model):
    message_text = models.CharField(max_length=256)
    start_mailing = models.DateTimeField()
    stop_mailing = models.DateTimeField()
    tag = models.CharField(max_length=64, null=True)
    code = models.CharField(max_length=3, null=True)
    is_active = models.BooleanField(default=True)

    def delete(self):
        self.is_active = False
        self.save()


class MessageStatus(models.Model):
    name = models.CharField(max_length=32)


class Message(models.Model):
    sending_time = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(MessageStatus, on_delete=models.DO_NOTHING)
    mailing_list_id = models.ForeignKey(MailingList, on_delete=models.CASCADE)
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    # is_active = models.BooleanField(default=True)
    #
    # def delete(self):
    #     self.is_active = False
    #     self.save()










