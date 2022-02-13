from rest_framework import serializers
from .models import *



class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ["first_name", "last_name", "melli_code","gender", "father_name", 'phone_number', 'workplace_number','mobile_number',
				  'province', 'city', 'address', "email"]
		extra_kwargs = {'mobile_number': {'required': False}}


