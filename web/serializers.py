from django.contrib.auth.models import User, Group
from rest_framework import serializers

from web.models import Statue


class StatueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statue
        fields = '__all__'