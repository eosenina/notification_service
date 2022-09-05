from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from client.models import Client
from client.serializers import ClientModelSerializer


class ClientModelViewSet(ModelViewSet):
    queryset = Client.objects.all().filter(is_active=True)
    # queryset = Client.objects.all().values('id', 'phone', 'code', 'timezone', 'tags')
    serializer_class = ClientModelSerializer
