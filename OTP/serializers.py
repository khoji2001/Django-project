from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import *
from django.contrib.auth import get_user_model

auth_user = get_user_model()


class MobileCodeSerializer(ModelSerializer):
	melli_code = serializers.CharField(max_length=10, required=False)
	new_password = serializers.CharField(max_length=50, required=False)
	class Meta:
		model = MobileCode
		fields = "__all__"
		extra_kwargs = {'token': {'required': False,'validators':[]}, 'verified': {'required': False}, 'mobile_number': {'required': False,'validators':[]}}


class UserRegistrationSerializer(ModelSerializer):
	class Meta:
		model = auth_user
		fields = ["first_name", "last_name", "melli_code","gender", "father_name", 'phone_number', 'workplace_number',
				  'province', 'city', 'address', "email"]
