from django.db import models


class Client(models.Model):
    phone = models.CharField(max_length=11, unique=True)
    code = models.CharField(max_length=3)
    timezone = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def delete(self):
        self.is_active = False
        self.save()


class ClientTag(models.Model):
    client_id = models.ForeignKey(Client, related_name='tags', on_delete=models.CASCADE)
    tag = models.CharField(max_length=64)

    def __str__(self):
        return self.tag


