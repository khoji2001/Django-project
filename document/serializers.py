from rest_framework.serializers import ModelSerializer, ValidationError
from .models import *


class CustomerDocumentSerializer(ModelSerializer):
	def validate(self,data):
		try:
			ss = data.get('caccount_turnover')
			if not ss.name.split('.')[1] in ['xlsx','xls']:
				raise ValidationError({'Error': 'لطفا فایل اکسل را آپلود نمایید'})
		except:
			pass
		return data
	class Meta:
		model = customer_document
		fields = "__all__"
		extra_kwargs = {'credit_rate': {'required': True}, 'mellicard_front': {'required': True}}

class SuretyDocumentSerializer(ModelSerializer):
	class Meta:
		model = surety_document
		fields = "__all__"

class ContractDocumentSerializer(ModelSerializer):
	class Meta:
		model = contract_document
		fields = "__all__"