from django.db.models import Count
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from mailing_list.models import Message, MailingList
from mailing_list.serializers import MailingListModelSerializer


class MailingListModelViewSet(ModelViewSet):
    queryset = MailingList.objects.all().filter(is_active=True)
    serializer_class = MailingListModelSerializer


class TotalMailingStatAPIView(APIView):
    def get(self, request):
        stat = Message.objects.values('status__name').annotate(total=Count('id'))
        mailing_lists_count = MailingList.objects.filter(is_active=True).aggregate(total=Count('id'))
        return Response({'total_mailing_lists': mailing_lists_count['total'], 'messages': stat})


class MailingStatAPIView(APIView):
    def get(self, request, list_id):
        stat = Message.objects.filter(mailing_list_id=list_id).values('status__name').annotate(total=Count('id'))
        return Response({'mailing_list_id': list_id, 'messages': stat})
