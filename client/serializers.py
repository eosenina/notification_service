from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer, Serializer
from client.models import Client, ClientTag


class ClientTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientTag
        fields = ('tag',)


class ClientModelSerializer(ModelSerializer):
    tags = ClientTagSerializer(many=True, allow_null=True)

    class Meta:
        model = Client
        fields = ('id', 'phone', 'code', 'timezone', 'tags')
        read_only_fields = ['code']

    def validate_phone(self, value):
        if len(value) != 11:
            raise serializers.ValidationError("The phone number is not correct. 11 digits expected.")
        elif not str(value).isdigit():
            raise serializers.ValidationError("The phone number is not correct. Only digits expected.")
        elif value[0] != '7':
            raise serializers.ValidationError("The phone number is not correct. It should starts with 7.")
        return value

    def create(self, validated_data):

        tags_data = validated_data.pop('tags')
        validated_data['code'] = validated_data['phone'][1:4]
        client = Client.objects.create(**validated_data)
        for tag in tags_data:
            ClientTag.objects.create(client_id=client, **tag)

        return client

    def update(self, instance, validated_data):
        validated_data['code'] = validated_data['phone'][1:4]
        tags_data = validated_data.pop('tags')
        client = super().update(instance, validated_data)

        old_tags = ClientTag.objects.filter(client_id=client.id)
        old_tags.delete()
        for tag in tags_data:
            ClientTag.objects.create(client_id=client, **tag)
        return client
