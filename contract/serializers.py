from supplier.models import supplier
from rest_framework.serializers import ModelSerializer,ValidationError
from rest_framework import serializers
from rest_framework.fields import empty
from .models import *
from extensions import jalali
from datetime import timedelta
from django.utils import timezone
from datetime import date

INSTALMENT_DETAIL_CHOICES = (
	('0' , 'delayed'),
	('1' , 'in_time'),
	('2' , 'off_time'),
	('3' , 'not_arrive')
)
class PaymentSerializer(ModelSerializer):
	class Meta:
		model = payment
		fields = ['amount','date']
class ContractCustSerializer(ModelSerializer):
	instalment_amount = serializers.IntegerField()
	total_amount_of_instalments = serializers.IntegerField()
	instalment_start_date  = serializers.DateField()
	end_date = serializers.DateField()
	remaining_amount = serializers.IntegerField()
	debit_amount = serializers.IntegerField()
	number_of_pays  = serializers.IntegerField()
	has_factor = serializers.SerializerMethodField('has_factor_func')
	is_signed = serializers.SerializerMethodField('is_signed_func')
	clear_receipt =  serializers.SerializerMethodField('clear_receipt_func')
	final_c =  serializers.SerializerMethodField('final_c_func')
	supp_c =  serializers.SerializerMethodField('supp_c_func')
	cust_c =  serializers.SerializerMethodField('cust_c_func')
	status = serializers.SerializerMethodField('validated_status')
	clearing_amount = serializers.SerializerMethodField('supplier_balance')

	def supplier_balance(self,obj):
		if obj.status in ['3','4','5']:
			return obj.supplier_balance
	def has_factor_func(self, obj):
		if obj.status == '2':
			try:
				obj.contract_document.final_invoice
				return True
			except:
				return False
	def is_signed_func(self, obj):
		supplier_type = self.context.get("supplier_type")
		if supplier_type == '1':
			if obj.sign_date == date.today():
				return True
			else:
				return False
	
	def validated_status(self,obj):
		if obj.status == '21':
			return '2'
		return obj.status
	def clear_receipt_func(self, obj):
		if obj.clearing_date != None:
			return "/contract/supp/{}/clear_receipt/pdf".format(obj.pk)
	def final_c_func(self, obj):
		supplier_type = self.context.get("supplier_type")
		if supplier_type == '1' and obj.sign_date == date.today() and obj.status == '1':
			return "/contract/supp/{}/final_c/pdf".format(obj.pk)
	def supp_c_func(self, obj):
		supplier_type = self.context.get("supplier_type")
		if supplier_type == '1' and obj.sign_date == date.today() and obj.status == '1':
			return "/contract/supp/{}/supp_c/pdf".format(obj.pk)
	def cust_c_func(self, obj):
		supplier_type = self.context.get("supplier_type")
		if supplier_type == '1' and obj.sign_date == date.today() and obj.status == '1':
			return "/contract/supp/{}/cust_c/pdf".format(obj.pk)

	class Meta:
		model = contract
		fields = ['id',"sign_date","invoice_date","description","net_amount","number_of_instalment",
		"downpayment","status", "supplier_name","contract_id","vcc_number","customer","supplier","vcc" 
		,"customer_fullname", "clearing_date" ,"clearing_amount",'instalment_amount','total_amount_of_instalments',
		'instalment_start_date','end_date','remaining_amount','debit_amount','number_of_pays',
		'has_factor', 'is_signed', 'clear_receipt', 'final_c','supp_c','cust_c']

class ContractPaymentsSerializer(ModelSerializer):
	payments = PaymentSerializer(many = True , read_only = True)
	class Meta:
		model = contract
		fields = ['payments']

class ContractInstalmentsSerializer(ModelSerializer):
	instalment_detail = serializers.SerializerMethodField('instalment_detail_func')

	def instalment_detail_func(self,obj):
		try:
			pays = (obj.payments.all().order_by('date'))
			total_pay = 0
			l = []
			ok = 0
			real_tot = 0
			for pay in pays:
				real_tot += pay.amount
				total_pay += pay.amount
				
				if ok <= obj.number_of_instalment :
					x = total_pay // obj.instalment_amount
					total_pay = total_pay - (x*obj.instalment_amount)
					for i in range(x):
						l.append(pay.date)
						ok += 1
			zero = obj.number_of_instalment - len(l)
			for i in range(zero):
				l.append('0')
		except Exception as e:
			print(str(e))
		
		try:
			pays = list(obj.payments.all().order_by('date'))
			pay_pointer = 0
			pay_amount = 0
			total_difference = 0
			amount = obj.vcc.amount
			penalty_status = obj.vcc.new_status
			instalment_date = obj.instalment_start_date
			instalment_amount = obj.instalment_amount
			number = amount // instalment_amount
			details = {}
			details["instalments"] = []
			for i in range(obj.number_of_instalment):
				temp = jalali.Gregorian(instalment_date).persian_tuple()
				#compute delta time for monday of next work week from signdate
				if temp[1] < 7: #first half of year
					delta_2 = timedelta(days=31)
				elif temp[1] == 12: #esfand month
					if temp[0] % 4 == 3: #kabise year
						delta_2 = timedelta(days=30)
					else: #not kabise
						delta_2 = timedelta(days=29)
				else: #second half of year and not esfand
					delta_2 = timedelta(days=30)
				if pay_pointer < len(pays):
					while pays[pay_pointer].date <= instalment_date:
						pay_amount += pays[pay_pointer].amount
						pay_pointer += 1
						if pay_pointer == len(pays):
							break
				data = {}
				data["clearing_date"] = l[i]
				data["date"] = instalment_date
				if data["clearing_date"] != '0':
					data["difference"] = (data["clearing_date"] - data["date"]).days
				else:
					data["difference"] = (timezone.now().date() - data["date"]).days
				if i < number:
					data["status"] = '1'
				elif instalment_date <= timezone.now().date():
					data["status"] = '2'
				else:
					data["status"] = '3'
					data["difference"] = 0
				total_difference += data["difference"]
				instalment_date += delta_2
				details["instalments"].append(data)
			pay_detail = obj.instalment_detail
			if penalty_status == '1':
				penalty_amount = 0
			else:
				penalty_amount = pay_detail[0]
			pay_status = pay_detail[1]
			details["amount"] = persian_numbers_converter(instalment_amount,'price')
			details["remain_amount"] = persian_numbers_converter(obj.remaining_amount(),'price')
			details["penalty_amount"] = persian_numbers_converter(penalty_amount,'price')
			details["total_diff"] = persian_numbers_converter(total_difference,'price')
			details['pay_status'] = pay_status
			return details
		except Exception as e:
			print(str(e))
	class Meta:
		model = contract
		fields = ['instalment_detail',]

class ContractSerializer(ModelSerializer):
	
	status = serializers.SerializerMethodField('validated_status')
	clearing_amount = serializers.SerializerMethodField('supplier_balance')
	def validated_status(self,obj):
		if obj.status == '21':
			return '2'
		return obj.status
	def supplier_balance(self,obj):
		if obj.status in ['3','4','5']:
			return obj.supplier_balance
	
	def validate(self, data ):
		fac = {
		'1': 'max_fac1',
		'2': 'max_fac2',
		'3': 'max_fac3',
		'4':'max_fac4'
	}
		try:
			if data['customer'].status not in ['0','1','3'] or data['customer'].level == '0':
				raise ValidationError("متقاضی تایید نشده است یا مدارک ناقص است")
			elif (data['net_amount'] - data['downpayment']) > 1000000 * getattr(supplier.objects.get(pk = data['supplier']),fac[data['customer'].level]):
				raise ValidationError("سقف تسهیلات رعایت نشده است")
			elif data['downpayment'] > data['net_amount'] * 0.7:
				raise ValidationError("پیش پرداخت بیش تر از حد مجاز")
		except ValidationError as v:
			raise ValidationError(list(v)[0])
		except:
			pass
		return data
	class Meta:
		model = contract
		fields = ['id',"sign_date","invoice_date" ,"invoice_number","description" , "clearing_date", "clearing_amount",
		"net_amount","number_of_instalment","customer_fullname","appoint_time",
		"downpayment","status", "supplier_name","contract_id","vcc_number","customer","supplier","vcc"]
		extra_kwargs = {'appoint_time': {'required': False}}


class ContractobjSerializer(ModelSerializer):
	def show(self,data):
		l = []
		for pk in data:
			l += [contract.objects.get(pk = pk)]
		return l
	class Meta:
		model = contract
		fields = '__all__'

