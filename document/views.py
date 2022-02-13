from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.mail import EmailMessage
from customer.models import surety,customer, Guarantee
from contract.models import contract
from supplier.permissions import IsSupplier
from supplier.models import *
from .models import *
from .serializers import *
from extensions import jalali
from OTP.models import Emails
from extensions.utill import persian_numbers_converter
CREDIT_EMAIL_CUST_HEADER = """
متقاضی: {0}
کدملی: {1}
تامین کننده: {2}
تاریخ ثبت نام: {3}
"""
CREDIT_EMAIL_SURT_HEADER = """
ضامن ایشان {0} با کد ملی {1}
"""
CREDIT_CUST_EMAIL_TEXT = """
 {0}- دارای پرونده قبلی 
 شماره قرارداد و شماره کارت به شرح زیر است:
 نام تامین کننده: {1}
 شماره کارت: {2}
 شماره قرارداد: {3}
 وضعیت قرارداد: {4}
"""
CREDIT_SURT_EMAIL_TEXT = """
 {0}- ضامن پرونده قبلی  
 شماره قرارداد و شماره کارت به شرح زیر است:
 نام تامین کننده: {1}
 شماره کارت: {2}
 شماره قرارداد: {3}
 وضعیت قرارداد: {4}
"""
ZERO_COUNT = """
دارای پرونده در قبلی در فرمیران نبودند.
"""
ZERO_SURT_COUNT = """
ضامن پرونده قبلی نبودند.
"""
def send_credit_email(Type,customer_melli_code,full_name,melli_code,date_joined,s_name = 'انتخاب نشده',surety_name = ''):
	date_string = persian_numbers_converter(jalali.Gregorian(date_joined.date()).persian_string("{}/{}/{}"))
	email_text = CREDIT_EMAIL_CUST_HEADER.format(full_name,customer_melli_code,s_name,date_string)
	if Type is 's':
		email_text += CREDIT_EMAIL_SURT_HEADER.format(surety_name,melli_code)
	i = 0
	for c in contract.objects.filter(customer__melli_code = melli_code):
		i += 1
		email_text += CREDIT_CUST_EMAIL_TEXT.format(str(i),c.supplier_name,c.vcc_number,c.contract_id,c.get_status_display())
	if i == 0:
		email_text += ZERO_COUNT
	i = 0
	for s in customer.objects.filter(melli_code = melli_code):
		for c in s.contracts.all():
			i += 1
			c = c.cont
			email_text += CREDIT_SURT_EMAIL_TEXT.format(str(i),c.supplier_name,c.vcc_number,c.contract_id,c.get_status_display())
	if i == 0:
		email_text += ZERO_SURT_COUNT
	email_dict = {
                'name' : full_name,
                's_name' : s_name,
                }
	emaill = Emails.objects.get(email_type = '7')
	email = EmailMessage(subject = emaill.ST.format(**email_dict),body = email_text ,from_email = 'admin@faramtestiran.com', to = [x.strip() for x in emaill.TO.split(',')] ,headers= {'Content_Type' :'text/plain'})
	email.send()
class CustomerDocumentView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request):
		user = request.user
		try:
			cust = user.customer
			try:
				document = customer_document.objects.get(customer=cust)
				serializer = CustomerDocumentSerializer(document)
				return Response(serializer.data, status.HTTP_200_OK)
			except:
				return Response({}, status.HTTP_404_NOT_FOUND)

		except Exception as e:
			try:
				s = user.supplier
				cust = customer.objects.get(pk = request.GET.get("customer"))
				document = customer_document.objects.get(customer=cust)
				serializer = CustomerDocumentSerializer(document)
				return Response(serializer.data, status.HTTP_200_OK)
			except Exception as w:
				return Response({}, status.HTTP_404_NOT_FOUND)
	
	def post(self, request):
		data = dict(request.data.items())
		user = request.user
		try:
			Customer = user.customer
			data["customer"] = Customer.id
			serializer = CustomerDocumentSerializer(data=data)
			if serializer.is_valid():
				Customer.save()
				serializer.save()
				try:
					Customer.customer_document.credit_rate
					send_credit_email('c',Customer.melli_code,Customer.full_name(),user.melli_code,user.date_joined)
				except:
					pass
				return Response(serializer.data, status.HTTP_201_CREATED)
			return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			try:
				s = user.supplier
				Customer = customer.objects.get(pk = data["customer"])
				serializer = CustomerDocumentSerializer(data=data)
				if serializer.is_valid():
					Customer.save()
					serializer.save()
					try:
						Customer.customer_document.credit_rate
						send_credit_email('c',Customer.melli_code,Customer.full_name(),Customer.user.melli_code,Customer.user.date_joined,s.name)
					except:
						pass
					return Response(serializer.data, status.HTTP_201_CREATED)
				return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
			except Exception as w:
				return Response({"Error": str(e) + str(w)},status.HTTP_404_NOT_FOUND)
	def put(self, request):
		user = request.user
		data = dict(request.data.items())
		try:
			Customer = user.customer
			if Customer.status == '2':
				return Response({"Error" : "پس از رد توسط مجری اعمال تغییرات مجاز نیست"} , status.HTTP_403_FORBIDDEN)
			data["customer"] = Customer.id
			try:
				document = customer_document.objects.get(customer=Customer)
			except:
				return Response({"Error": "قبلا مدرکی بارگذاری نکردید"},status.HTTP_404_NOT_FOUND)
			data["mellicard_front"] = data.get("mellicard_front", document.mellicard_front)
			data["credit_rate"] = data.get("credit_rate", document.credit_rate)
			serializer = CustomerDocumentSerializer(document, data=data)
			if serializer.is_valid():
				Customer.save()
				serializer.save()
				return Response(serializer.data, status.HTTP_200_OK)
			return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			try:
				s = user.supplier
				Customer = customer.objects.get(pk = data["customer"])
				document = customer_document.objects.get(customer=Customer)
				data["mellicard_front"] = data.get("mellicard_front", document.mellicard_front)
				data["credit_rate"] = data.get("credit_rate", document.credit_rate)
				serializer = CustomerDocumentSerializer(document, data=data)
				if serializer.is_valid():
					Customer.save()
					serializer.save()
					return Response(serializer.data, status.HTTP_200_OK)
				return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
			except Exception as w:
				return Response({"Error": str(e) + str(w)}, status.HTTP_404_NOT_FOUND)


class SuretyDocumentView(APIView):
	permission_classes = [IsAuthenticated]
	
	def get(self, request): 
		surety_order = request.GET.get("surety_order") 
		if request.GET.get("surety_order") is None:
			return Response({"Error" : "ترتیب ضامن ضروری است"} , status.HTTP_400_BAD_REQUEST)
		user = request.user
		try:
			user.customer
			try:
				g = Guarantee.objects.filter(customer = user)
				g = g[int(surety_order)]
				try:
					document = customer_document.objects.get(customer = g.surety_id)
					serializer = CustomerDocumentSerializer(document)
					return Response(serializer.data, status.HTTP_200_OK)
				except:
					return Response({'customer': g.surety_id}, status.HTTP_404_NOT_FOUND)
			except:
				return Response({"Error": "ضامنی ثبت نشده است"}, status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			try:
				supp = user.supplier
				customer = supp.customer.get(pk = request.GET.get("customer"))
				g = Guarantee.objects.filter(customer = customer)
				g = g[int(surety_order)]
				try:
					document = customer_document.objects.get(customer = g.surety_id)
					serializer = CustomerDocumentSerializer(document)
					return Response(serializer.data, status.HTTP_200_OK)
				except:
					return Response({'customer': g.surety_id}, status.HTTP_404_NOT_FOUND)
			except Exception as w:
				return Response({"Error": "ضامنی ثبت نشده است"}, status.HTTP_400_BAD_REQUEST)
	
	def post(self, request):
		user = request.user
		data = dict(request.data.items())
		if data.get("suretyID") is None:
			return Response({"Error" : "شناسه ضامن ضروری است"} , status=status.HTTP_400_BAD_REQUEST)
		surety_id = data.pop("suretyID")
		try:
			Customer = user.customer
			try:
				g = Guarantee.objects.get(customer = user, surety_id=surety_id)
			except:
				return Response({"Error": "این ضامن برای شما ثبت نشده است."}, status.HTTP_400_BAD_REQUEST)
			s = g.surety
			data["customer"] = surety_id
			serializer = CustomerDocumentSerializer(data= data)
			if serializer.is_valid():
				try:
					Customer.customer_document
					Customer.status = '0'
				except:
					Customer.status = '00'
				Customer.save()
				serializer.save()
				send_credit_email('s',Customer.melli_code,Customer.full_name(),s.melli_code,user.date_joined,surety_name=s.full_name())
				return Response(serializer.data, status.HTTP_201_CREATED)
			return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			try:
				supp = user.supplier
				Customer = supp.customer.get(pk = data.pop("customer"))
				g = Guarantee.objects.get(customer= Customer, surety_id= data.pop("suretyID"))
				s = g.surety
				data["customer"] = g.surety_id
				serializer = CustomerDocumentSerializer(data= data)
				if serializer.is_valid():
					try:
						Customer.customer_document
						Customer.status = '0'
					except:
						Customer.status = '00'
					Customer.save()
					serializer.save()	
					send_credit_email('s',Customer.melli_code,Customer.full_name(),s.melli_code,Customer.user.date_joined,supp.name,s.full_name())
					return Response(serializer.data, status.HTTP_201_CREATED)
				return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
			except Exception as w:
				return Response({"Error": str(e) + str(w)}, status.HTTP_404_NOT_FOUND)

	def put(self, request):
		user = request.user
		data = dict(request.data.items())
		if data.get("suretyID", None) is None:
			return Response({"Error": "شناسه ضامن ضروری است"}, status.HTTP_400_BAD_REQUEST)
		surety_id = data.pop("suretyID")
		try:
			Customer = user.customer
			if Customer.status == '2':
				return Response({"Error" : "پس از رد توسط مجری اعمال تغییرات مجاز نیست"} , status.HTTP_403_FORBIDDEN)
			try:
				g = Guarantee.objects.get(customer=Customer, surety_id= surety_id)
			except:
				return Response({"Error": "این ضامن برای شما ثبت نشده است."}, status.HTTP_400_BAD_REQUEST)
			s = g.surety
			data['customer'] = surety_id
			try:
				document = customer_document.objects.get(customer = g.surety_id)
			except:
				return Response({"Error": "این ضامن قبلا مدرکی ثبت نکرده است"}, status.HTTP_400_BAD_REQUEST)
			serializer = CustomerDocumentSerializer(document, data=data, partial=True)
			if serializer.is_valid():
				try:
					Customer.customer_document
					Customer.status = '0'
				except:
					Customer.status = '00'
				Customer.save()
				serializer.save()
				return Response(serializer.data, status.HTTP_200_OK)
			return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			try:
				supp = user.supplier
				Customer = supp.customer.get(pk = data.pop("customer"))
				g = Guarantee.objects.get(customer=Customer, surety_id = data.pop("suretyID"))
				s = g.surety
				data['customer'] = g.surety_id
				document = customer_document.objects.get(customer = g.surety_id)
				serializer = CustomerDocumentSerializer(document, data=data, partial = True)

				if serializer.is_valid():
					try:
						Customer.customer_document
						Customer.status = '0'
					except:
						Customer.status = '00'
					Customer.save()
					serializer.save()
					return Response(serializer.data, status.HTTP_200_OK)
				return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
			except Exception as w:
				return Response({"Error": str(e) + str(w)}, status.HTTP_404_NOT_FOUND)

class ContractDocumentView(APIView):
	permission_classes = [IsAuthenticated, IsSupplier]
	def get(self,request):
		if request.GET.get("contractID") is None:
			return Response({"Error" : "شناسه قرارداد ضروری است"} , status=status.HTTP_400_BAD_REQUEST)
		contractID = request.GET.get("contractID")
		try:
			c = contract.objects.get(pk = contractID)
			document = contract_document.objects.get(contract = c)
			serializer = ContractDocumentSerializer(document)
			return Response(serializer.data, status.HTTP_200_OK)
		except Exception as e:
			return Response({"Error": str(e)}, status.HTTP_404_NOT_FOUND)

	def post(self, request):
		data = dict(request.data.items())

		if data.get("contractID") is None:
			return Response({"Error" : "شناسه قرارداد ضروری است"} , status=status.HTTP_400_BAD_REQUEST)
		try:
			c = contract.objects.get(pk = data.pop("contractID"))
			data["contract"] = c.id
			serializer = ContractDocumentSerializer(data = data)
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data, status.HTTP_201_CREATED)
			return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({"Error": str(e)}, status.HTTP_404_NOT_FOUND)

	def put(self, request):
		data = dict(request.data.items())

		if data.get("contractID", None) is None:
			return Response({"Error": "شناسه قرارداد ضروری است"}, status.HTTP_400_BAD_REQUEST)

		try:
			c = contract.objects.get(pk = data.pop("contractID"))
			data["contract"] = c.id
			document = contract_document.objects.get(contract = c)
			serializer = ContractDocumentSerializer(document, data=data)
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data, status.HTTP_200_OK)
			return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({"Error": str(e)}, status.HTTP_404_NOT_FOUND)
