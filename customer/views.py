from io import StringIO
from users.views import main_calculation
from config.settings import BASE_DIR
from document.models import contract_directory_path, contract_document, customer_directory_path
from functools import partial
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view , schema , permission_classes
from rest_framework.schemas import AutoSchema
from django.contrib.auth.decorators import user_passes_test
from mailmerge import MailMerge
import os
from zipfile import ZipFile
from os.path import basename


from .permissions import IsCustomer
from .models import Guarantee, customer, surety , customer_info
from .serializers import *
from contract.serializers import ContractCustSerializer
from contract.models import LOAN_LEVEL, contract
from django.shortcuts import render
from django.http import JsonResponse,HttpResponse,FileResponse
from users.models import User
from supplier.models import supplier
from .forms import Uploadcustexcel
import openpyxl
import json
from django.views.decorators.csrf import csrf_exempt

OUTPUTS_DIR = os.path.join(BASE_DIR,"outputs")
# Create your views here.
@csrf_exempt		
def old_calculator(request):
	calc_out = {}

	if request.method == 'POST':
		data = json.loads(request.body)
		net_amount = data['net_amount'] #مبلغ فاکتور
		number_of_instalment = data['number_of_instalment'] #تعداد اقساط
		additional_costs = 0 #هزینه های اضافی
		try:
			s = supplier.objects.get(id = data['supplier_id'])
			
			downpayment_rate = data.get('downpayment_rate',s.downpayment_rate) #(نسبت پیش پرداخت (بین ۰-۱

			discount = s.discount # تخفیف
			
			financial_source_rate = s.coffer.financial_source_rate1 # نرخ خرید پول

			if number_of_instalment <=12:
				company_gain_rate = s.company_gain_rate_one # کارمزد توسعه
				financial_source_rate = s.coffer.financial_source_rate1 # نرخ خرید پول
			else:
				company_gain_rate = s.company_gain_rate_two
				financial_source_rate = s.coffer.financial_source_rate2 # نرخ خرید پول
			investor_gain_rate = s.investor_gain_rate # کارمزد بازاریاب
			warranty_gain_rate = s.issuer.warranty_gain_rate # کارمزد صدور ضمانت نامه
			share_rate = s.issuer.share_rate # سهم توسعه از کارمزد صدور ضمانت نامه
			
		except KeyError:
			downpayment_rate = data.get('downpayment_rate',0.25) #(نسبت پیش پرداخت (بین ۰-۱
			discount = 0 # تخفیف
			financial_source_rate = 0.31 # نرخ خرید پول
			company_gain_rate = 0.025 # کارمزد توسعه
			investor_gain_rate = 0 # کارمزد بازاریاب
			warranty_gain_rate = 0.02 # کارمزد صدور ضمانت نامه
			share_rate = 0.5 # سهم توسعه از کارمزد صدور ضمانت نامه
		except:

			return JsonResponse({"Error" : "فروشگاه مورد نظر یافت نشد"})
		
		calc_out['discounted_net_amount'] = int(round(net_amount *(1 - discount) , -4)) #مبلغ فاکتور پس از تخفیف

		calc_out['downpayment'] = int(round(net_amount * downpayment_rate , -4)) # پیش پرداخت

		calc_out['loan_face_value'] = net_amount - calc_out['downpayment']
		if calc_out['loan_face_value'] <= LOAN_LEVEL['1']:
			calc_out['level'] = '1'
			calc_out['level_str'] = 'سطح ۱'
			calc_out['suretys'] = 'یک ضامن'
		elif calc_out['loan_face_value'] <= LOAN_LEVEL['2']:
			calc_out['level'] = '2'
			calc_out['level_str'] = 'سطح ۲'
			calc_out['suretys'] = 'یک ضامن'
		elif calc_out['loan_face_value'] <= LOAN_LEVEL['3']:
			calc_out['level'] = '3'
			calc_out['level_str'] = 'سطح ۳'
			calc_out['suretys'] = 'دو ضامن'
		else:
			
			return JsonResponse({"Error" : "مبلغ بیش از حد مجاز"})
		calc_out['supplier_balance'] = int(round(calc_out['discounted_net_amount'] - calc_out['downpayment'] , -4)) #تسویه ی فروشگاه

		calc_out['company_gain'] = int(round(net_amount * company_gain_rate))
		
		calc_out['investor_gain'] = int(round(net_amount * investor_gain_rate))
		
		month = number_of_instalment
		head = (month + 1 ) / 24
		source_percent = financial_source_rate * 100
		source = source_percent / 1200
		rate = (1 + source) ** month
		warranty_rate = source * rate * warranty_gain_rate * month * head
		calc_out['warranty_gain'] = int(round( warranty_rate * (calc_out['company_gain'] + calc_out['investor_gain']+ calc_out['supplier_balance']) 
                            / (rate * (1 - source * month * warranty_gain_rate * head * share_rate) - 1)))

		calc_out['complete_gain'] = calc_out['company_gain'] + calc_out['investor_gain'] + calc_out['warranty_gain'] * share_rate

		calc_out['loan_amount'] = calc_out['complete_gain'] + calc_out['supplier_balance'] + additional_costs

		calc_out['instalment_amount'] = calc_out['loan_amount'] * source * rate / (rate - 1)
		temp = int(round(calc_out['instalment_amount'] , -4))
		if temp - calc_out['instalment_amount'] < -1000:
			calc_out['instalment_amount'] = temp + 5000
		else:
			calc_out['instalment_amount'] = temp

		calc_out['total_amount_of_instalments'] = calc_out['instalment_amount'] * number_of_instalment

		calc_out['customer_check'] = int(round(calc_out['total_amount_of_instalments'] * 1.1 , -6)) + 1000000

		if calc_out['loan_face_value'] <= 80000000:
			calc_out['surety_check'] = 0
		else:
			calc_out['surety_check'] = int(round(calc_out['total_amount_of_instalments']  * 1.5 , -6)) + 1000000
		calc_out['total_amount'] = int(calc_out['instalment_amount'] * number_of_instalment + 
        calc_out['downpayment'])
	
	return JsonResponse(calc_out)
@api_view(['POST'])
def calculator(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		net_amount = data['net_amount'] #مبلغ فاکتور
		number_of_instalment = data['number_of_instalment'] #تعداد اقساط
		additional_costs = 0 #هزینه های اضافی
		try:
			s = request.user.supplier
		except:
			s = supplier.objects.get(status = True)
			
		data['downpayment_rate'] = data.get('downpayment_rate',s.downpayment_rate) #(نسبت پیش پرداخت (بین ۰-۱
		data['discount'] = s.discount # تخفیف
		if number_of_instalment <=12:
			data['company_gain_rate'] = s.company_gain_rate_one # کارمزد توسعه
			data['financial_source_rate'] = s.coffer.financial_source_rate1 # نرخ خرید پول
		else:
			data['company_gain_rate'] = s.company_gain_rate_two
			data['financial_source_rate'] = s.coffer.financial_source_rate2 # نرخ خرید پول

		data['investor_gain_rate'] = s.investor_gain_rate # کارمزد بازاریاب
		data['warranty_gain_rate'] = s.issuer.warranty_gain_rate # کارمزد صدور ضمانت نامه
		data['share_rate'] = s.issuer.share_rate # سهم توسعه از کارمزد صدور ضمانت نامه
		data['additional_costs'] = additional_costs
		data['suretys'] = {
			'1' : s.fac1_desc,
   			'2' : s.fac2_desc,
			'3' : s.fac3_desc,
			'4' : s.fac4_desc,
		}
		data['loan_level'] = {
			'1' : s.max_fac1 * 1000000,
   			'2' : s.max_fac2 * 1000000,
			'3' : s.max_fac3 * 1000000,
			'4' : s.max_fac4 * 1000000,
		}
		my_calc = main_calculation(data)
		x = my_calc.customer()
		return JsonResponse(x)

@user_passes_test(lambda u : u.is_staff)
def customer_file(request, c_id , type):
	destination = os.path.join(OUTPUTS_DIR,"customers")
	if not os.path.exists(destination):
		os.makedirs(destination)
	source = os.path.join(BASE_DIR,"contract_docs/input/customer_file.docx")
	try:
		cust = customer.objects.get(pk = c_id)
		Customer = customer_info(cust)
		doc_destination = os.path.join(destination,f'{c_id}مشتری.docx')
		docxMerge(vars(Customer),source,doc_destination , destination)
		pdf_destination = os.path.join(destination,f'{c_id}مشتری.pdf')
		if (type == 'doc'):
			return FileResponse(open(doc_destination,'rb'),as_attachment = True)
		elif (type == 'pdf'):
			if os.path.exists(pdf_destination):
				response = FileResponse(open(pdf_destination,'rb'),as_attachment = True) 
				return response
			else:
				return HttpResponse("اطلاعات متقاضی یا تامین کننده ناقص است")
		else:
			return HttpResponse("404")
	except Exception as e:
		return HttpResponse(str(e))
@user_passes_test(lambda u : u.is_staff)
def all_doc(request, c_id , type):


	cust = customer.objects.get(pk = c_id)
	surety = Guarantee.objects.filter(customer=cust)
	Contract = contract.objects.filter(customer=cust)
	name_of_file = cust.melli_code

	has_customer_info = 0
	has_surety_info = 0
	has_contract_info = 0
	try:
		contract_docs = contract_document.objects.filter(contract=Contract[0])
	except:
		Contract = 0

	if Contract != 0 and len(Contract) > 0:
		name_of_file = str(Contract[0].contract_id)

	
	if not os.path.exists("customer_doc/"):
		os.makedirs("customer_doc")
	all_doc_destination = "customer_doc/"+name_of_file+'.zip'
	zip_doc = ZipFile(all_doc_destination, 'w')
	#user_documents_zip
	with ZipFile('user_doc.zip', 'w') as zipObj:
		try:
			for folderName, subfolders, filenames in os.walk(os.path.join(BASE_DIR ,"media/")+customer_directory_path(customer_document.objects.get(customer= cust))):
				for filename in filenames:
					has_customer_info = 1
					#create complete filepath of file in directory
					filePath = os.path.join(folderName, filename)
					# Add file to zip
					zipObj.write(filePath, basename(filePath))
		except:
			pass
	if has_customer_info == 1:
		zip_doc.write('user_doc.zip')
	os.remove('user_doc.zip')

	#surety_documents_zip	
	if len(surety) > 0:	
		for index,sur in enumerate(surety):
			name_of_zip_file ='surety_doc'+ str(index+1) +'.zip' 
			with ZipFile(name_of_zip_file, 'w') as zipObj:
				customer_id = sur.surety 
				try:
					for folderName, subfolders, filenames in os.walk(os.path.join(BASE_DIR ,"media/")+customer_directory_path(customer_document.objects.get(customer=customer_id))):
						for filename in filenames:
							has_surety_info = 1
							#create complete filepath of file in directory
							filePath = os.path.join(folderName, filename)
							# Add file to zip
							zipObj.write(filePath, basename(filePath))
				except:
					pass
			if has_surety_info == 1:
				zip_doc.write(name_of_zip_file)
			has_surety_info = 0
			os.remove(name_of_zip_file)	
							
	#contract_ducoments_zip
	if Contract != 0 and len(Contract) > 0:
		for index, contract_doc in enumerate(contract_docs):
			name_of_zip_file = 'contract_doc'+ str(index+1)  +'.zip' 
			with ZipFile(name_of_zip_file, 'w') as zipObj:
				try:
					for folderName, subfolders, filenames in os.walk(os.path.join(BASE_DIR ,"media/")+contract_directory_path(contract_doc)):
						for filename in filenames:
							has_contract_info = 1
							#create complete filepath of file in directory
							filePath = os.path.join(folderName, filename)
							# Add file to zip
							zipObj.write(filePath, basename(filePath))
				except:
					pass
			if has_contract_info == 1:
				zip_doc.write(name_of_zip_file)
			has_contract_info = 0
			os.remove(name_of_zip_file)	
	zip_doc.close()
	return FileResponse(open(all_doc_destination,'rb'),as_attachment = True)
		


def docxMerge(context,source,destination,pdf_dest): #mailmerge source docx template and generate contract
	template = source
	document = MailMerge(template)
	document.merge(**context)
	document.write(destination)
	document.close()
	os.system ("libreoffice --headless --convert-to pdf --outdir "+ pdf_dest + " "+ destination)

def Help(request):
	source = os.path.join(BASE_DIR,"contract_docs/input/customer_help.pdf")
	return FileResponse(open(source,'rb'),as_attachment = True)

SUPPLIERS = {
	0 : "بازنشستگان" ,
	3 : "جهیزیه " ,
	5 : " فدک" ,
def addcustomers(request):
	if request.method == 'POST':
		cust_form = Uploadcustexcel(request.POST , request.FILES)
		customers = {}
		if cust_form.is_valid():
			cust_excel = request.FILES['file']
			wb = openpyxl.load_workbook(cust_excel)
			for val in SUPPLIERS.values():
				worksheet = wb[val]
				mobilenumbers = worksheet['G']
				first_names = worksheet['E']
				last_names = worksheet['F']
				father_names = worksheet['AA']
				jobs = worksheet['H']
				estimate_incomes = worksheet['I']
				melli_codes = worksheet['AB']
				provinces = worksheet['AC']
				cities = worksheet['AD']
				addresses = worksheet['AE']
				phonenumbers = worksheet['AW']
				phonecodes = worksheet['AX']
				worknumbers = worksheet['AY']
				workcodes = worksheet['AZ']
				surety1_firstname = worksheet['AL']
				surety1_lastname = worksheet['AM']
				surety1_father = worksheet['AN']
				surety1_mellicode = worksheet['AO']
				surety1_mobilenumber = worksheet['AP']
				surety1_job = worksheet['AQ']
				surety1_estimateincome = worksheet['AR']
				surety1_province = worksheet['AS']
				surety1_city = worksheet['AT']
				surety1_address = worksheet['AU']
				surety1_phonenumber = worksheet['AW']
				surety1_phonecode = worksheet['AX']
				surety1_worknumber = worksheet['AY']
				surety1_workcode = worksheet['AZ']
				surety2_firstname = worksheet['BB']
				surety2_lastname = worksheet['BC']
				surety2_father = worksheet['BD']
				surety2_mellicode = worksheet['BE']
				surety2_mobilenumber = worksheet['BF']
				surety2_job = worksheet['BG']
				surety2_estimateincome = worksheet['BH']
				surety2_province = worksheet['BI']
				surety2_city = worksheet['BJ']
				surety2_address = worksheet['BK']
				surety2_phonenumber = worksheet['BM']
				surety2_phonecode = worksheet['BN']
				surety2_worknumber = worksheet['BO']
				surety2_workcode = worksheet['BP']
				status = '1'
				level = '1'
				for j in range(1,len(mobilenumbers)):
					level = '1'
					if (mobilenumbers[j].value != None):
						first_name =  first_names[j].value
						last_name = last_names[j].value
						father_name = father_names[j].value
						melli_code = melli_codes[j].value
						province = provinces[j].value
						city = cities[j].value
						address = addresses[j].value
						try:
							u = User.objects.get(mobile_number = mobilenumbers[j].value)
						except:
							u = User.objects.create(mobile_number = mobilenumbers[j].value)
						u.first_name = first_name if first_name != None else ''
						u.last_name = last_name if last_name != None else ''
						u.father_name = father_name if father_name != None else ''
						u.melli_code = melli_code if melli_code != None else ''
						u.province = province if province != None else ''
						u.city = city if city != None else ''
						u.address = address if address != None else ''
						u.phone_number = str(phonecodes[j].value) + str(phonenumbers[j].value) if phonecodes[j].value != None else ''
						u.workplace_number = str(workcodes[j].value) + str(worknumbers[j].value) if workcodes[j].value != None else ''
						u.save()
						u.set_password(u.melli_code)
						u.save()
						if (surety1_mellicode[j].value != None and len(str(surety1_mellicode[j].value)) > 1):
							level = '2'
						if (surety2_mellicode[j].value != None and len(str(surety2_mellicode[j].value)) > 1):
							level = '3'
						try:
							c = customer.objects.get(user = u)
						except:
							c = customer.objects.create(user = u,status = status,level = level)
						job = jobs[j].value
						c.job = job if job != None else ''
						estimate_income = estimate_incomes[j].value
						if estimate_income != None and str(estimate_income) != '-':
							c.estimate_income = int(estimate_income) * 10000000
						c.save()
						if int(level) >= 2:
							firstname =	surety1_firstname[j].value
							lastname =	surety1_lastname[j].value
							father =	surety1_father[j].value
							mellicode =	surety1_mellicode[j].value
							mobilenumber =	surety1_mobilenumber[j].value
							job =	surety1_job[j].value
							estimateincome = surety1_estimateincome[j].value
							province =	surety1_province[j].value
							city =	surety1_city[j].value
							address =	surety1_address[j].value
							phonenumber =	surety1_phonenumber[j].value
							phonecode =	surety1_phonecode[j].value
							worknumber =surety1_worknumber[j].value
							workcode =	surety1_workcode[j].value
							try:
								s = surety.objects.get(melli_code = mellicode)
							except:
								s = surety.objects.create(customer = c)
							if (mobilenumber != None ):
								s.mobile_number = mobilenumber
							if (firstname != None ):
								s.first_name = firstname
							if( lastname != None ):
								s.last_name = lastname
							if (father != None ):
								s.father_name = father
							if( mellicode != None ):
								s.melli_code = mellicode
							if( province != None):
								s.province = province
							if (city != None ):
								s.city = city
							if( address != None ):
								s.address = address
							if (phonecode != None ):
								s.phone_number = str(phonecode) + str(phonenumber)
							if( workcode != None ):
								s.workplace_number = str(workcode) + str(worknumber)
							if job != None:
								s.job = job
							if estimateincome != None and str(estimateincome) != '-':
								s.estimate_income = int(estimateincome) * 10000000
							s.save()
							if level == '3':
								firstname =	surety2_firstname[j].value
								lastname =	surety2_lastname[j].value
								father =	surety2_father[j].value
								mellicode =	surety2_mellicode[j].value
								mobilenumber =	surety2_mobilenumber[j].value
								job =	surety2_job[j].value
								estimateincome = surety2_estimateincome[j].value
								province =	surety2_province[j].value
								city =	surety2_city[j].value
								address =	surety2_address[j].value
								phonenumber =	surety2_phonenumber[j].value
								phonecode =	surety2_phonecode[j].value
								worknumber =surety2_worknumber[j].value
								workcode =	surety2_workcode[j].value
								try:
									s2 = surety.objects.get(melli_code = mellicode)
								except:
									s2 = surety.objects.create(customer = c)
								if (mobilenumber != None ):
									s2.mobile_number = mobilenumber
								if (firstname != None ):
									s2.first_name = firstname
								if( lastname != None ):
									s2.last_name = lastname
								if (father != None ):
									s2.father_name = father
								if( mellicode != None ):
									s2.melli_code = mellicode
								if( province != None):
									s2.province = province
								if (city != None ):
									s2.city = city
								if( address != None ):
									s2.address = address
								if (phonecode != None ):
									s2.phone_number = str(phonecode) + str(phonenumber)
								if( workcode != None ):
									s2.workplace_number = str(workcode) + str(worknumber)
								if job != None :
									s2.job = job
								if estimateincome != None and str(estimateincome) != '-':
									s2.estimate_income = int(estimateincome) * 10000000
								s2.save()				
			return HttpResponse("موفق باشید")
	else:
		cust_form = Uploadcustexcel()
		return render(request, 'cust_upload.html', { 'cust_form' : cust_form , })


class CustomerRegistrationView(APIView):
	def has_permission(self, request, view):
		if request.method == 'POST':
			return True
		elif bool(request.user and request.user.is_authenticated):
			return True
		return False
	def get(self, request):
		user = request.user
		try:
			s = user.supplier
			if request.GET.get("customerID") is None:
				return Response({"Error" : "شناسه متقاضی ضروری است"} , status=status.HTTP_400_BAD_REQUEST)
			my_customer = s.customer.get(pk = request.GET.get("customerID"))
			serializer = CustomerDetailSerializer(my_customer)
			return Response(serializer.data, status.HTTP_200_OK)

		except Exception as e:
			try:
				my_customer = customer.objects.get(user = user)
				serializer = CustomerDetailSerializer(my_customer)
				return Response(serializer.data, status.HTTP_200_OK)
			except Exception as e:
				return Response({"error": str(e)}, status.HTTP_404_NOT_FOUND)
	
	def post(self, request):
		data = dict(request.data.items())
		user = request.user
		try:
			s = user.supplier
			if data.get("customerMellicode") is not None:
				try:
					customer_user = User.objects.get(melli_code = data.pop("customerMellicode"))
					if len(customer.objects.filter(user=customer_user)) > 0:
						Customer = customer.objects.get(user = customer_user)
						s.customer.add(Customer)
						serializer = CustomerDetailSerializer(Customer)
						return Response({"message": "متقاضی به مشتریان شما اضافه شد" , "data" : serializer.data}, status.HTTP_200_OK)
				except Exception as e:
					return Response({"Error" : str(e)} , status.HTTP_404_NOT_FOUND)
			try:
				data['status'] = '00'
				serializer = CustomerDetailSerializer(data=data)
				if serializer.is_valid():
					c = serializer.save()
					c.user.set_password(c.password)
					c.user.save()
					s.customer.add(c)
					return Response(serializer.data, status.HTTP_201_CREATED)
				return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				return Response({"Error" : str(e)} , status.HTTP_406_NOT_ACCEPTABLE)
		except Exception as e:
			
			data['status'] = '00'
			serializer = CustomerDetailSerializer(data=data)
			if serializer.is_valid():
				c = serializer.save()
				c.user.set_password(c.password)
				c.user.save()
				return Response(serializer.data, status.HTTP_201_CREATED)
			return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
	
	def put(self, request):
		data = dict(request.data.items())
		user = request.user
		try:
			s = user.supplier
			if data.get("customerID") is None:
				return Response({"Error" : "شناسه متقاضی ضروری است"} , status=status.HTTP_400_BAD_REQUEST)
			my_customer = s.customer.get( pk = data.pop("customerID"))
			if my_customer.status == '2':
					return Response({"Error" : "پس از رد توسط مجری اعمال تغییرات مجاز نیست"} , status.HTTP_403_FORBIDDEN)
			if my_customer.status in ['1','3'] and my_customer.level == data.get('level',my_customer.level):
					return Response({"Error" : "پس از تایید توسط مجری اعمال تغییرات مجاز نیست"} , status.HTTP_403_FORBIDDEN)
			try:
				my_customer.customer_document
				for s in my_customer.suretys.all():
					s.surety_document
				data['status'] = '0'
			except:
				data['status'] = '00'
			if data.get("user") == None:
				data['user'] = my_customer.user.id
				serializer = CustomerDetailSerializer(my_customer , data = data, partial=True)
			else:
				if data['user'].get('mobile_number') != None:
					del (data['user']['mobile_number'])
				serializer = CustomerDetailSerializer(my_customer, data=data,partial=True)
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data, status.HTTP_200_OK)
			else:
				return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			try:
				my_customer = customer.objects.get(user = user)
				if my_customer.status == '2':
					return Response({"Error" : "پس از رد توسط مجری اعمال تغییرات مجاز نیست"} , status.HTTP_403_FORBIDDEN)
				if my_customer.status in ['1','3'] and my_customer.level == data.get('level',my_customer.level):
						return Response({"Error" : "پس از تایید توسط مجری اعمال تغییرات مجاز نیست"} , status.HTTP_403_FORBIDDEN)
				try:
					my_customer.customer_document
					for s in my_customer.suretys.all():
						s.surety_document
					data['status'] = '0'
				except:
					data['status'] = '00'
				serializer = CustomerDetailSerializer(my_customer , data = data, partial=True)
				if serializer.is_valid():
					serializer.save()
					return Response(serializer.data, status.HTTP_200_OK)
				return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				return Response({"Error": str(e)}, status.HTTP_404_NOT_FOUND)

class ContractViewSet(viewsets.ModelViewSet):

    pagination_class = PageNumberPagination
    permission_classes = [IsCustomer, IsAuthenticated]
    serializer_class = ContractCustSerializer
    queryset = supplier.objects.filter(status=True)

    def list(self,request):
        try:
            c = request.user.customer
            queryset = c.contract_set.all()
            serializer = self.get_serializer(queryset , many = True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"Error" : str(e)} , status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsCustomer])
@schema(AutoSchema())
def add_supplier(request):
	data = dict(request.data.items())
	if data.get("supplierID") is None:
		return Response({"error" : "شناسه تامین کننده ضروری است"}, status.HTTP_400_BAD_REQUEST)
	try:
		c = customer.objects.get(user = request.user)
		s = supplier.objects.get(pk = data.get("supplierID"))
		s.customer.add(c)
		s.save()
		return Response({'message' : "تامین کننده برای متقاضی ثبت شد"}, status.HTTP_200_OK)
	except Exception as e:
		return Response({"Error" : str(e)} , status.HTTP_404_NOT_FOUND)

def add_surety(request, customer_id):

	pass

class SuretyRegistrationView(APIView):
	permission_classes = [IsAuthenticated]
	
	def get(self, request):
		surety_mellicode = request.GET.get("surety_mellicode") 
		surety_order = request.GET.get("surety_order") 
		customer_id = request.GET.get("customerID") 
		user = request.user
		try:
			if surety_mellicode is not None:
				try:
					cust = request.user.customer
				except:
					sup = request.user.supplier
					cust = sup.customer.get(pk = int(customer_id))
				
				try:
					if surety_mellicode == cust.melli_code:
						return Response({"Error" : "نمیتوانید ضامن خودتان باشید"} , status=status.HTTP_400_BAD_REQUEST)
					surety = customer.objects.get(melli_code = surety_mellicode)
					try:
						Guarantee.objects.get(customer= cust, surety=surety)
						return Response({"Error" : "این کد ملی قبلا ضامن شما بوده است"} , status=status.HTTP_400_BAD_REQUEST)
					except:
						g = Guarantee()
						g.surety = surety
						g.customer = cust
						g.save()
					# add to guarantee table
						serializer = CustomerDetailSerializer(surety)
						return Response(serializer.data, status.HTTP_200_OK)
				# 404
				except Exception as e:
					return Response({"error": str(e)}, status.HTTP_404_NOT_FOUND)
			if surety_order is None:
				return Response({"Error" : "ترتیب ضامن ضروری است"} , status=status.HTTP_400_BAD_REQUEST)
			if surety_order not in ['0', '1']:
				return Response({"Error" : "ترتیب ضامن 0 یا 1 میتواند باشد"} , status=status.HTTP_400_BAD_REQUEST)

			Customer = user.customer
			g_surties = Guarantee.objects.filter(customer=Customer)
			if len(g_surties) == 0:
				return Response({} , status=status.HTTP_200_OK)			
			g = g_surties[int(surety_order)]
			s = g.surety
			####
			serializer = CustomerDetailSerializer(s)
			return Response(serializer.data, status.HTTP_200_OK)
		except Exception as e:
			try:
				s = user.supplier
				
				if customer_id is None:
					return Response({"Error" : "شناسه متقاضی ضروری است"} , status=status.HTTP_400_BAD_REQUEST)
				Customer = s.customer.get(pk = int(customer_id))
				g = Guarantee.objects.filter(customer=Customer)[int(surety_order)]
				s = g.surety
				####
				serializer = CustomerDetailSerializer(s)
				
				return Response(serializer.data, status.HTTP_200_OK)
			except Exception as e:
				return Response({"error": str(e)}, status.HTTP_404_NOT_FOUND)
	
	def post(self, request):
		data = dict(request.data.items())
		user = request.user
		try:
			Customer = user.customer
		
			serializer = CustomerDetailSerializer(data=data)
			if serializer.is_valid():
				Customer.status = '00'
				Customer.save()
				surety_obj = serializer.save()
				Guarantee.objects.create(customer= Customer, surety_id=surety_obj.id)
				return Response(serializer.data, status.HTTP_201_CREATED)
			return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
		except Exception as w:
			try:
				s = user.supplier
				if data.get("customerID") is None:
					return Response({"Error" : "شناسه متقاضی ضروری است"} , status=status.HTTP_400_BAD_REQUEST)
				Customer = s.customer.get(pk = data.pop("customerID"))
				
				serializer = CustomerDetailSerializer(data=data)
				if serializer.is_valid():
					Customer.status = '00'
					Customer.save()
					surety_obj = serializer.save()
					Guarantee.objects.create(customer= Customer, surety_id=surety_obj.id)
					return Response(serializer.data, status.HTTP_201_CREATED)
				return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				return Response({"error": str(e) + str(w)}, status.HTTP_404_NOT_FOUND)

	def put(self,request):
		data = dict(request.data.items())
		
		user = request.user
		melli_code = data.get("melli_code")
		if melli_code == None:
			return Response({"Error" : "کد ملی ضامن ضامن ضروری است"} , status=status.HTTP_400_BAD_REQUEST)

		try:
			Customer = user.customer
			if Customer.status == '2':
					return Response({"Error" : "پس از رد توسط مجری اعمال تغییرات مجاز نیست"} , status.HTTP_403_FORBIDDEN)
			if Customer.status in ['1','3']:
					return Response({"Error" : "پس از تایید توسط مجری اعمال تغییرات مجاز نیست"} , status.HTTP_403_FORBIDDEN)
			
			melli_code = data.get("melli_code")
			surety = customer.objects.get(melli_code=melli_code)
			g = Guarantee.objects.get(customer= Customer, surety_id=surety)
			s = g.surety
		
			serializer = CustomerDetailSerializer(s, data=data, partial=True)
			if serializer.is_valid():
				try:
					Customer.customer_document
					for g in Guarantee.objects.filter(customer= Customer):
						s = g.surety 
						s.customer_document
					Customer.status = '0'
				except:
					Customer.status = '00'
				Customer.save()
				serializer.save()
				return Response(serializer.data, status.HTTP_200_OK)
			return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			try:
				s = user.supplier
				if data.get("customerID") is None:
					return Response({"Error" : "شناسه متقاضی ضروری است"} , status=status.HTTP_400_BAD_REQUEST)
				Customer = s.customer.get(pk = data.pop("customerID"))
				if Customer.status == '2':
					return Response({"Error" : "پس از رد توسط مجری اعمال تغییرات مجاز نیست"} , status.HTTP_403_FORBIDDEN)
				if Customer.status in ['1','3']:
					return Response({"Error" : "پس از تایید توسط مجری اعمال تغییرات مجاز نیست"} , status.HTTP_403_FORBIDDEN)
			
				surety = customer.objects.get(melli_code= melli_code)
				g = Guarantee.objects.get(customer= Customer, surety= surety)
				s = g.surety
				####
				serializer = CustomerDetailSerializer(s ,data = data, partial=True)
				if serializer.is_valid():
					try:
						Customer.customer_document
						for g in Guarantee.objects.filter(customer= Customer):
							s = g.surety 
							s.customer_document
						Customer.status = '0'
					except:
						Customer.status = '00'
					Customer.save()
					serializer.save()
					return Response(serializer.data, status.HTTP_200_OK)
				return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				return Response({"error": str(e)}, status.HTTP_404_NOT_FOUND)
