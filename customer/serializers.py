from rest_framework.serializers import ModelSerializer,PrimaryKeyRelatedField
from rest_framework import serializers
from .models import customer, surety,Family,Financial_Information,PersonalHome,OrganizationHome,RentalHome,Check_information
from document.models import customer_document,surety_document
from users.serializers import UserSerializer


class SuretySerializer(ModelSerializer):
	ice_url = serializers.SerializerMethodField('get_ice_url')
	def get_ice_url(self,obj):
		try:
			doc = obj.surety_document.credit_rate
			return doc.url
		except:
			return None
	class Meta:
		model = surety
		fields = "__all__"
class FamilySerializer(ModelSerializer):
	class Meta:
		model = Family
		fields = '__all__'
		extra_kwargs = {'customer': {'required': False}}
class Financial_InformationSerializer(ModelSerializer):
	class Meta:
		model = Financial_Information
		fields = '__all__'
		extra_kwargs = {'customer': {'required': False}}
class PersonalHomeSerializer(ModelSerializer):
	class Meta:
		model = PersonalHome
		fields = '__all__'
		extra_kwargs = {'customer': {'required': False},
		'page_number': {'required': False , 'validators': []}}
class OrganizationHomeSerializer(ModelSerializer):
	class Meta:
		model = OrganizationHome
		fields = '__all__'
		extra_kwargs = {'customer': {'required': False}}
class RentalHomeSerializer(ModelSerializer):
	class Meta:
		model = RentalHome
		fields = '__all__'
		extra_kwargs = {'customer': {'required': False},
		'is_mine': {'required': False , 'validators': []},
		'rental_rate': {'required': False ,'validators': []},
		'due_date': {'required': False ,'validators': []}}
class CheckInformationSerializer(ModelSerializer):
	class Meta:
		model = Check_information
		fields = '__all__'
		extra_kwargs = {'customer': {'required': False},
		'sayyad_number': {'validators': []}}

STATUS_RANK = {
	'3' : ('get_accept_reason_display','accept_desc'),
 	'5' : ('get_faultdocument_reason_display','faultdocument_desc'),
	'6' : ('get_expire_reason_display','expire_desc'),
	'4' : ('get_cancel_reason_display','cancel_desc'),
	'2' : ('get_reject_reason_display','reject_desc')
}
class CustomerDetailSerializer(ModelSerializer):
	family = FamilySerializer(many = False,required=False,allow_null = True)
	financial = Financial_InformationSerializer(many = False,required=False,allow_null = True)
	personalhome = PersonalHomeSerializer(many = False,required=False,allow_null = True)
	organizationhome = OrganizationHomeSerializer(many = False,required=False,allow_null = True)
	rentalhome = RentalHomeSerializer(many = False,required=False,allow_null = True)
	checkinfo = CheckInformationSerializer(many = False,required=False,allow_null = True)
	contract_status = serializers.SerializerMethodField('last_contract_status')
	ice_url = serializers.SerializerMethodField('get_ice_url')
	credit_rank = serializers.SerializerMethodField('get_credit_rank')
 
	def get_credit_rank(self,obj):
		new_rank = ''
		if obj.status in STATUS_RANK.keys():
			reason,desc = STATUS_RANK[obj.status]
			if getattr(obj,reason)() != None:
				new_rank += getattr(obj,reason)() + ' : '
				new_rank += '\nو '.join(x.title for x in getattr(obj,desc).all()) + '          '
		new_rank += obj.credit_rank
		return new_rank
	def last_contract_status(self, obj):
		supplier_id = self.context.get("supplier_id")
		if supplier_id:
			qs = obj.contract_set.filter(supplier__pk = supplier_id).order_by('-id')
			if len(qs) > 0:
				if qs[0].status == '21':
					return '2'
				return qs[0].status
			else:
				return '9'
		else:
			qs = obj.contract_set.all().order_by('-id')
			if len(qs) > 0:
				if qs[0].status == '21':
					return '2'
				return qs[0].status
			else:
				return '9'

	def get_ice_url(self,obj):
		try:
			doc = obj.customer_document.credit_rate
			return doc.url
		except:
			return None
	def update(self , instance, validated_data):
		try:
			user_data = dict(validated_data.pop('user'))
			user = instance.user
			for attr, value in user_data.items():
				setattr(user, attr, value)
			user.save()
		except Exception as e:
			pass
		try:
			family_data = dict(validated_data.pop('family'))
			try:
				family = instance.family
			except:
				family = Family(customer=instance)
			for attr, value in family_data.items():
				setattr(family, attr, value)
			family.save()
		except Exception as e:
			pass
		try:
			financial_data = dict(validated_data.pop('financial'))			
			try:
				financial = instance.financial
			except:
				financial = Financial_Information(customer=instance)
			for attr, value in financial_data.items():
				setattr(financial, attr, value)
					
			financial.save()
		except Exception as e:
			pass
		try:
			personal_data = dict(validated_data.pop('personalhome'))
			try:
				personal = instance.personalhome
			except:
				personal = PersonalHome(customer=instance)
			for attr, value in personal_data.items():
				setattr(personal, attr, value)
			personal.save()
		except Exception as e:
			pass
		try:
			organ_data = dict(validated_data.pop('organizationhome'))
			try:
				organ = instance.organizationhome
			except:
				organ = OrganizationHome(customer=instance)
			for attr, value in organ_data.items():
				setattr(organ, attr, value)
			organ.save()
		except Exception as e:
			pass
		try:
			rental_data = dict(validated_data.pop('rentalhome'))
			try:
				rental = instance.rentalhome
			except:
				rental = RentalHome(customer=instance)
			for attr, value in rental_data.items():
				setattr(rental, attr, value)
			rental.save()
		except Exception as e:
			pass
		try:
			check_data = dict(validated_data.pop('checkinfo'))
			try:
				check = instance.checkinfo
			except:
				check = Check_information(customer=instance)
			for attr, value in check_data.items():
				setattr(check, attr, value)
			check.save()
		except Exception as e:
			pass
		for attr, value in validated_data.items():
			setattr(instance, attr, value)
		instance.save()
		return instance
	
	def create(self, validated_data):
		family_data = None
		user_data = None
		financial_data = None
		personal_data = None
		organ_data = None
		rental_data = None
		check_data = None
		if validated_data.get('family') != None:
			family_data = dict(validated_data.pop('family'))

		if validated_data.get('user') != None:
			user_data = dict(validated_data.pop('user'))

		if validated_data.get('financial') != None:
			financial_data = dict(validated_data.pop('financial'))
		
		if validated_data.get('personalhome') != None:
			personal_data = dict(validated_data.pop('personalhome'))

		if validated_data.get('organizationhome') != None:
			organ_data = dict(validated_data.pop('organizationhome'))
		
		if validated_data.get('rentalhome') != None:
			rental_data = dict(validated_data.pop('rentalhome'))

		if validated_data.get('checkinfo') != None:
			check_data = dict(validated_data.pop('checkinfo'))
		
		cust = super().create(validated_data)
		
		if user_data != None:
			f = cust.user
			for attr, value in user_data.items():
					setattr(f, attr, value)
			f.save()

		if family_data != None:
			f = Family(customer=cust)
			
			for attr, value in family_data.items():
					setattr(f, attr, value)
			f.save()
		if financial_data != None:
			f = Financial_Information(customer=cust)
			for attr, value in financial_data.items():
					setattr(f, attr, value)
			f.save()
		if personal_data != None:
			f = PersonalHome(customer=cust)
			for attr, value in personal_data.items():
					setattr(f, attr, value)
			f.save()
		if organ_data != None:
			f = OrganizationHome(customer=cust)
			for attr, value in organ_data.items():
					setattr(f, attr, value)
			f.save()
		if rental_data != None:
			f = RentalHome(customer=cust)
			for attr, value in rental_data.items():
					setattr(f, attr, value)
			f.save()
		if check_data != None:
			f = Check_information(customer=cust)
			for attr, value in check_data.items():
					setattr(f, attr, value)
			f.save()
		return cust 
			
	class Meta:
		model = customer
		fields = "__all__"
		extra_kwargs = {'password': {'write_only': True}}


class CustomerSerializer(ModelSerializer):

	family = FamilySerializer(many = False,required=False, allow_null=True)
	def create(self, validated_data):
		try:
			family_data = dict(validated_data.pop('family'))
			cust = super().create(validated_data)
			f = Family(customer=cust)
			for attr, value in family_data.items():
				setattr(f, attr, value)
			f.save()
			return cust
		except:
			return super().create(validated_data) 
	class Meta:
		model = customer
		fields = "__all__"
		extra_kwargs = {'password': {'write_only': True}}
