from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from mailing_list.models import Message, MailingList


class MessageModelSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class MailingListModelSerializer(ModelSerializer):
    class Meta:
        model = MailingList
        fields = ('id', 'message_text', 'start_mailing', 'stop_mailing', 'tag', 'code')

    def validate(self, attrs):
        if attrs['start_mailing'] > attrs['stop_mailing']:
            raise serializers.ValidationError("End date must be after start date.")
        return attrs
