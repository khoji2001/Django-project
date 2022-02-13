from rest_framework import serializers
from .models import *

class SupplierSerializer(serializers.ModelSerializer):
	class Meta:
		model = supplier
		fields = ["name","website_url" ,"phone_number" ,"status" ,"Type" ,"fcategory" ,"province" 
		,"city" ,"address" ,"downpayment_rate" ,"discount" ,"contract_code" ,"accountant_name" 
		,"account_bank" ,"account_shaba"]

class SupplierShowcaseSerializer(serializers.ModelSerializer):
	class Meta:
		model = supplier
		fields = ["name", "website_url", "phone_number",'province' , 'city' , 'address', "fcategory"]

class InitialSupplierSerializer(serializers.Serializer):
	agent_firstname = serializers.CharField(max_length = 40)
	agent_lastname = serializers.CharField(max_length = 40)
	agent_mobile_number = serializers.CharField(max_length = 11)
	brand = serializers.CharField(max_length = 40)
	phone_number = serializers.CharField(max_length = 11)
	province = serializers.CharField(max_length = 40)
	city = serializers.CharField(max_length = 40)
	address = serializers.CharField(max_length = 200)
	description = serializers.CharField(max_length = 200)

	def create(self, validated_data):
		return abstract_supplier(**validated_data)

NUMBER_PAY_DICT = {
    2 : ([1],{ 1 : (2,)}),
    3 : ([1,3],{1 : (3,), 3 : (1,2,3)}),
    4 : ([2,4],{ 2 :(2,4), 4 :(1,2,3,4)}),
    5 : ([2],{ 2 : (2,5)}),
    6 : ([2,3],{ 2 : (3,6), 3 :(2,4,6)}),
    7 : ([3],{ 3 : (2,4,7)}),
    8 : ([4,3],{ 4 : (2,4,6,8), 3 : (2,5,8)}),
    9 : ([3],{ 3 : (3,6,9)}),
    10 : ([4],{ 4 : (2,4,7,10)}),
    12 : ([4],{ 4 : (3,6,9,12)}),
}
LEVEL_DICT = {
    1 : 120000000,
    2 : 150000000,
    3 : 300000000,
    4 : 1000000000
}
class SpeciaCalcInput:
	def __init__(self,**kwargs):
		self.net_amount = kwargs['net_amount']
		self.face_net_amount = kwargs['face_net_amount']
		self.sign_date = kwargs['sign_date']
		self.duration = kwargs['duration']
		self.num_of_pay = kwargs['num_of_pay']
		self.level = kwargs['level']
		self.additional_costs = kwargs['additional_costs']
		self.downpayment_rate = kwargs['downpayment_rate']
		self.discount = kwargs['discount']
		self.financial_source_rate = kwargs['financial_source_rate']
		self.company_gain_rate = kwargs['company_gain_rate']
		self.investor_gain_rate = kwargs['investor_gain_rate']
		self.warranty_gain_rate = kwargs['warranty_gain_rate']
		self.share_rate = kwargs['share_rate']

class SpecialCalcInputSerializer(serializers.Serializer):
	net_amount = serializers.IntegerField()
	face_net_amount = serializers.IntegerField(required=False)
	sign_date = serializers.DateField()
	duration = serializers.IntegerField()
	num_of_pay = serializers.IntegerField()
	level = serializers.ChoiceField(choices = [1,2,3,4])
	additional_costs = serializers.IntegerField()
	downpayment_rate = serializers.FloatField()
	discount = serializers.FloatField()
	financial_source_rate = serializers.FloatField()
	company_gain_rate = serializers.FloatField()
	investor_gain_rate = serializers.FloatField()
	warranty_gain_rate = serializers.FloatField()
	share_rate = serializers.FloatField()

	def create(self,validated_data):
		return SpeciaCalcInput(**validated_data)
	def validate_duration(self,value):
		if value not in NUMBER_PAY_DICT:
			raise serializers.ValidationError('دوره بازپرداخت صحیح نیست.')
		return value
	def validate_downpayment_rate(self,value):
		if value < 0.25:
			raise serializers.ValidationError('مبلغ پیش پرداخت کمتر از حد مجاز است.')
		return value
	def validate(self, data):
		if data['num_of_pay'] not in NUMBER_PAY_DICT[data['duration']][0]:
			raise serializers.ValidationError('تعداد پرداخت معتبر نیست.')
		if data['net_amount'] > LEVEL_DICT[data['level']] // 0.75:
			data['downpayment_rate'] = (data['net_amount'] - LEVEL_DICT[data['level']]) / data['net_amount']
			data['face_net_amount'] = LEVEL_DICT[data['level']] // 0.75
		else:
			data['face_net_amount'] = data['net_amount']
		return data
