
from users.views import main_calculation
from OTP.models import Emails
from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import pagination
from .models import supplier
from .permissions import IsSupplier
from config.settings import ADMIN_EMAILS
from contract.models import contract
from contract.serializers import ContractSerializer,ContractCustSerializer
from customer.permissions import IsCustomer
from customer.serializers import *
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_302_FOUND, HTTP_404_NOT_FOUND, \
HTTP_201_CREATED
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view , schema , permission_classes
from rest_framework.schemas import AutoSchema
from datetime import datetime,date
from .serializers import *
import json
from extensions import jalali
from customer.models import Guarantee

# Create your views here.
@api_view(['POST'])
@permission_classes([IsSupplier])
@schema(AutoSchema())
def old_specialCalc(request):
    s = request.user.supplier
    data = dict(request.data.items())
    data['additional_costs'] = data.get('additional_costs',s.additional_costs)
    data['downpayment_rate'] = data.get('downpayment_rate',s.downpayment_rate)
    data['discount'] = data.get('discount',s.discount)
    data['financial_source_rate'] = data.get('financial_source_rate',s.coffer.financial_source_rate1)
    data['company_gain_rate'] = data.get('company_gain_rate',s.company_gain_rate_one)
    data['investor_gain_rate'] = data.get('investor_gain_rate',s.investor_gain_rate)
    data['warranty_gain_rate'] = data.get('warranty_gain_rate',s.issuer.warranty_gain_rate)
    data['share_rate'] = data.get('share_rate',s.issuer.share_rate)
    serializer = SpecialCalcInputSerializer(data = data)
    if serializer.is_valid():
        Input = serializer.save()
        calc_out = {}
        discounted_net_amount = int(round(Input.net_amount - Input.face_net_amount * Input.discount , -4)) #مبلغ فاکتور پس از تخفیف

        calc_out['downpayment'] = int(round(Input.net_amount * Input.downpayment_rate , -4)) # پیش پرداخت

        loan_face_value = Input.net_amount - calc_out['downpayment']

        supplier_balance = int(round(discounted_net_amount - calc_out['downpayment'] , -4)) #تسویه ی فروشگاه

        company_gain = int(round(Input.face_net_amount * Input.company_gain_rate))

        investor_gain = int(round(Input.face_net_amount * Input.investor_gain_rate))

        month = Input.num_of_pay
        head = (month + 1 ) / 24
        source_percent = Input.financial_source_rate * 100
        source = source_percent / 1200
        rate = (1 + source) ** month
        warranty_rate = source * rate * Input.warranty_gain_rate * month * head
        warranty_gain = int(round( warranty_rate * (company_gain + investor_gain + supplier_balance) 
                            / (rate * (1 - source * month * Input.warranty_gain_rate * head * Input.share_rate) - 1)))

        complete_gain = company_gain + investor_gain + warranty_gain * Input.share_rate

        loan_amount = complete_gain + supplier_balance + Input.additional_costs
        calc_out['loan_amount'] = loan_amount
        instalment_amount = loan_amount * source * rate / (rate - 1)

        calc_out['total_amount_of_instalments'] = instalment_amount * Input.num_of_pay
        calc_out['instalment_amount'] = calc_out['total_amount_of_instalments'] / Input.num_of_pay

        temp = int(round(calc_out['instalment_amount'] , -4))
        if temp - calc_out['instalment_amount'] < -1000:
            calc_out['instalment_amount'] = temp + 5000
        else:
            calc_out['instalment_amount'] = temp
        calc_out['total_amount_of_instalments'] = calc_out['instalment_amount'] * Input.num_of_pay
        calc_out['total_amount'] = int(calc_out['total_amount_of_instalments'] + calc_out['downpayment'])
        calc_out['check_dates'] = []
        pdate = jalali.Gregorian(Input.sign_date).persian_tuple()
        persian_date_format = '{}/{}/{}'
        for i in NUMBER_PAY_DICT[Input.duration][1][Input.num_of_pay]:
            year,month,day = pdate
            month  += i
            if month > 12:
                month -= 12
                year += 1
            if month==12 and day > 28:
                day = 28
            calc_out['check_dates'].append(persian_date_format.format(year,month,day))
        return JsonResponse(calc_out)
    else:
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


###########################################################
@api_view(['POST'])
@permission_classes([IsSupplier])
@schema(AutoSchema())
def specialCalc(request):
    fac = {
            '1': 'max_fac1',
            '2': 'max_fac2',
            '3': 'max_fac3',
            '4':'max_fac4'
        }
    s = request.user.supplier
    data = dict(request.data.items())
    data['additional_costs'] = data.get('additional_costs',s.additional_costs)
    data['downpayment_rate'] = data.get('downpayment_rate',s.downpayment_rate)
    data['discount'] = data.get('discount',s.discount)
    data['financial_source_rate'] = data.get('financial_source_rate',s.coffer.financial_source_rate1)
    data['finance_gain_rate'] = data.get('finance_gain_rate',s.coffer.finance_gain_rate)
    data['nokol_rate'] = data.get('nokol_rate',s.coffer.nokol_rate)
    data['company_gain_rate'] = data.get('company_gain_rate',s.company_gain_rate_one)
    data['investor_gain_rate'] = data.get('investor_gain_rate',s.investor_gain_rate)
    data['warranty_gain_rate'] = data.get('warranty_gain_rate',s.issuer.warranty_gain_rate)
    data['share_rate'] = data.get('share_rate',s.issuer.share_rate)
    serializer = SpecialCalcInputSerializer(data = data)
    if serializer.is_valid():
        Input = serializer.save()
        loan = getattr(s,fac[data.get('level','4')])
        max_loan = 1000000 * loan // 0.75
        
        if int(data['net_amount']) < max_loan:
            data['face_net_amount'] = int(data['net_amount'])
        else:
            data['face_net_amount'] = max_loan
        my_calc = main_calculation(data)
        x = my_calc.supp()
        return JsonResponse(x)
    else:
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
###########################################################

@api_view(['POST'])
@permission_classes([IsSupplier])
@schema(AutoSchema())
def old_calculator(request):
    calc_out = {}
    try:
        s = request.user.supplier
        if request.method == 'POST':
            data = json.loads(request.body)
            net_amount = data['net_amount'] #مبلغ فاکتور
            number_of_instalment = data['number_of_instalment'] #تعداد اقساط
            additional_costs = s.additional_costs #هزینه های اضافی
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

            calc_out['discounted_net_amount'] = int(round(net_amount *(1 - discount) , -4)) #مبلغ فاکتور پس از تخفیف

            calc_out['downpayment'] = int(round(net_amount * downpayment_rate , -4)) # پیش پرداخت

            calc_out['loan_face_value'] = net_amount - calc_out['downpayment']

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

            calc_out['complete_gain'] = calc_out['company_gain'] + calc_out['investor_gain'] + calc_out['warranty_gain']* share_rate

            calc_out['loan_amount'] = calc_out['complete_gain'] + calc_out['supplier_balance'] + additional_costs

            calc_out['instalment_amount'] = calc_out['loan_amount'] * source * rate / (rate - 1)
            temp = int(round(calc_out['instalment_amount'] , -4))
            if temp - calc_out['instalment_amount'] < -1000:
                calc_out['instalment_amount'] = temp + 5000
            else:
                calc_out['instalment_amount'] = temp

            calc_out['total_amount_of_instalments'] = calc_out['instalment_amount'] * number_of_instalment

            calc_out['customer_check'] = int(round(calc_out['total_amount_of_instalments'] * 1.1 , -6)) + 1000000

            
            calc_out['surety_check'] = int(round(calc_out['total_amount_of_instalments']  * 1.5 , -6)) + 1000000

            calc_out['total_amount'] = int(calc_out['instalment_amount'] * number_of_instalment + 
            calc_out['downpayment'])
            return JsonResponse(calc_out)

    except Exception as e:
        return HttpResponse(str(e))

@api_view(['POST'])
@permission_classes([IsSupplier])
@schema(AutoSchema())
def calculator(request):
    try:
        s = request.user.supplier
        if request.method == 'POST':
            data = json.loads(request.body)
            net_amount = data['net_amount'] #مبلغ فاکتور
            number_of_instalment = data['number_of_instalment'] #تعداد اقساط
            data['additional_costs'] = s.additional_costs #هزینه های اضافی
            data['downpayment_rate'] = data.get('downpayment_rate',s.downpayment_rate) #(نسبت پیش پرداخت (بین ۰-۱
            data['discount'] = s.discount # تخفیف
            data['financial_source_rate'] = s.coffer.financial_source_rate1 # نرخ خرید پول
            if number_of_instalment <=12:
                data['company_gain_rate'] = s.company_gain_rate_one # کارمزد توسعه
            else:
                data['company_gain_rate'] = s.company_gain_rate_two
            data['investor_gain_rate'] = s.investor_gain_rate # کارمزد بازاریاب
            data['warranty_gain_rate'] = s.issuer.warranty_gain_rate # کارمزد صدور ضمانت نامه
            data['share_rate'] = s.issuer.share_rate # سهم توسعه از کارمزد صدور ضمانت نامه

            my_calc = main_calculation(data)
            x = my_calc.supplier()
            return JsonResponse(x)

    except Exception as e:
        return HttpResponse(str(e))


class CustomerViewSet(viewsets.ModelViewSet):

    pagination_class = PageNumberPagination
    permission_classes = [IsSupplier, IsAuthenticated]
    serializer_class = CustomerDetailSerializer
    queryset = supplier.objects.filter(status=True)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        request = context.get('request')
        try:
            s = request.user.supplier
            context['supplier_id'] = s.id
        except:
            pass
        return context
    def list(self,request):
        c_status = str(request.GET.get("customerStatus"))
        try:
            s = request.user.supplier
            if (c_status == '1'):
                initial_queryset = s.customer.filter(status = c_status).order_by('-id')
                queryset = []
                for c in initial_queryset:
                    try:
                        contract.objects.get(supplier = s , customer = c , status__iexact = '0')
                    except Exception as e:
                        queryset.append(c)
            elif (c_status in ['0','2']):
                queryset = s.customer.filter(status = c_status).order_by('-id')
            else:
                queryset = s.customer.order_by('-id')
            serializer = self.get_serializer(queryset , many = True)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"Error","تامین کننده مورد نظر یافت نشد"} , status.HTTP_404_NOT_FOUND)
LEVEL = {
    '0' : 'مشخص نشده',
    '1' : 'سطح ۱',
    '2' : 'سطح ۲',
    '3' : 'سطح ۳',
}
class ContractViewSet(viewsets.ModelViewSet):

    pagination_class = PageNumberPagination
    permission_classes = [IsSupplier, IsAuthenticated]
    serializer_class = ContractSerializer
    queryset = supplier.objects.filter(status=True)
    
    def list(self,request):
        try:
            page_size = request.GET.get("page_size")
            if page_size != None:
                self.pagination_class.page_size = page_size
            s = request.user.supplier
            if request.GET.get("customerID") is None:
                queryset = s.contract_set.all().order_by("-id")
                          
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page,many = True)
                    return self.get_paginated_response(serializer.data)
                serializer = self.get_serializer(queryset, many = True)
            else:
                customer_id = int(request.GET.get("customerID"))
                queryset = s.contract_set.filter(customer__pk = customer_id).order_by("-id")
                page = self.paginate_queryset(queryset)
                if page is not None: 
                    serializer = ContractCustSerializer(page , many = True)
                    return self.get_paginated_response(serializer.data)
                serializer = ContractCustSerializer(queryset , many = True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"Error" : str(e)} , status.HTTP_404_NOT_FOUND)
    
    def create(self, request):
        s = request.user.supplier
        data = dict(request.data.items())
        data["supplier"] = s.id
        try:
            customer = s.customer.get(pk = data["customer"])
            Guarantee_objs = Guarantee.objects.filter(customer = customer)
            sureties_have_permission = Guarantee_objs.filter(surety__again_purchase = True)
            sureties_have_not_permission = Guarantee_objs.filter(surety__again_purchase = False)   
            false_surety = []
            for item in sureties_have_not_permission:
                false_surety += [item.surety.user.get_full_name()]
            false_surety = ','.join(false_surety)
            
            if len(Guarantee_objs) != len(sureties_have_permission):
                return Response({"Error" : "ضامن {} قابلیت عقد مجدد قرارداد را ندارد  ".format(false_surety)} , status.HTTP_400_BAD_REQUEST)
            if customer.again_purchase == False:
                return Response({"Error" : "متقاضی اجازه خرید مجدد ندارد."} , status.HTTP_403_FORBIDDEN)
            if data.get("appoint_time") != None and data.get("appoint_time") != '' :
                appoint_time = datetime.strptime(data['appoint_time'],"%Y-%m-%dT%H:%M")
                if appoint_time < datetime.now():
                    return Response({"Error" : "رزرو زمان گذشته ممکن نیست."} , status.HTTP_400_BAD_REQUEST)
            elif s.Type == '0':
                return Response({"Error" : "تعیین قرارملاقات ضروری است."} , status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    del(data["appoint_time"])
                    del(data["sign_date"])
                except:
                    pass
            
            if s.contract_set.filter(customer__pk = data["customer"]).count() > 0:
                return Response({"Error" : "اجازه تولید قرارداد با این متقاضی را ندارید"} , status.HTTP_400_BAD_REQUEST)
            if (s.Type == '0' and customer.status not in ['1','3']) or (s.Type == '1' and customer.status not in ['0','1','3']):
                return Response({"Error" : "متقاضی تایید نشده است."} , status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(data = data)
            if serializer.is_valid():
                
                Contract = serializer.save()
                for item in Guarantee_objs:
                    surt = item.surety
                    surt.again_purchase = False
                    surt.save()
                customer.again_purchase = False
                customer.save()
                    
                if Contract.appoint_time != None:
                    appoint.contract = Contract
                    appoint.save()
                else:
                    email_dict = {
                    'name' : Contract.customer.full_name(),
                    's_name' : s.name,
                    'level' : LEVEL[Contract.customer.level],
                    'time' : persian_numbers_converter(jalali.Gregorian(date.today()).persian_string('{}/{}/{}'))
                    }
                    emaill = Emails.objects.get(email_type = '4')
                    too = [x.strip() for x in emaill.TO.split(',')]
                    email = EmailMessage(subject = emaill.ST.format(**email_dict),body = emaill.ET.format(**email_dict) ,from_email = 'admin@test.com', to = too,headers= {'Content_Type' :'text/plain'})
                    email.send()
                return Response(serializer.data, status.HTTP_201_CREATED)
            return Response({"Error" : serializer.errors['non_field_errors'][0]}, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Error" : str(e)},status.HTTP_404_NOT_FOUND)

    def update(self, request, pk = None):
        s = request.user.supplier
        data = dict(request.data.items())
        data["supplier"] = s.id
        
        try:
            c = s.contract_set.get(pk = pk)
            serializer = self.get_serializer(c,data = data,partial = True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)} , status.HTTP_404_NOT_FOUND)

def categories(request):
    pass

def brands(request):
    pass

class SuppliersForCustomer(GenericAPIView):
    pagination_class = PageNumberPagination
    permission_classes = [IsCustomer, IsAuthenticated]
    serializer_class = SupplierShowcaseSerializer
    queryset = supplier.objects.filter(status=True)

    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializers = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializers.data)
            data = result.data
        else:
            serializers = self.get_serializer(page, many=True)
            data = serializers.data
        return Response(data, HTTP_200_OK)

class SupplierRegistrationView(APIView):

    def post(self,request):
        data = dict(request.data.items())
        serializer = InitialSupplierSerializer(data = data)
        if serializer.is_valid():
            try:
                serializer.save()
                email_text = """new supplier {brand} with phonenumber {phone_number} 
                 agent {agent_firstname} {agent_lastname} {agent_mobile_number} {province} {city} {address} 
                details : {description} """
                emaill = Emails.objects.get(email_type = '5')
                too = [x.strip() for x in emaill.TO.split(',')]
                email = EmailMessage(subject = emaill.ST,body = emaill.ET.format(**serializer.validated_data),from_email = 'admin@test.com', to = too,headers= {'Content_Type' :'text/plain'})
                email.send()
                return Response ({"message" : 'ثبت نام شما به مدیر سایت اطلاع داده شد'} , HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, HTTP_400_BAD_REQUEST)


class SupplierView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            my_supplier = user.supplier
            serializer = SupplierSerializer(my_supplier)
            return Response(serializer.data, HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, HTTP_404_NOT_FOUND)
