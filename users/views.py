
# from contract.models import LOAN_LEVEL
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
import openpyxl
import os
from extensions import jalali
from django.contrib.auth.decorators import user_passes_test
from .models import *
import json
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view , schema , permission_classes
from rest_framework.schemas import AutoSchema
from django.utils.translation import ugettext_lazy as _
from supplier.models import supplier
from customer.models import customer
from django.contrib.auth import authenticate
from rest_framework import exceptions
from numpy_financial import pmt
# Create your views here.
OUTPUT_DIR = os.path.join(settings.BASE_DIR,"contract_docs")
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
@api_view(['POST'])
@permission_classes([])
@schema(AutoSchema())
def old_calculator(request):
    calc_out = {}
    if request.method == 'POST':
        data = json.loads(request.body)
        net_amount = int(data['net_amount']) #مبلغ فاکتور
        number_of_instalment = int(data['number_of_instalment']) #تعداد اقساط
        additional_costs = int(data['additional_costs']) #هزینه های اضافی
        downpayment_rate = float(data['downpayment_rate']) #(نسبت پیش پرداخت (بین ۰-۱
        discount = float(data['discount']) # تخفیف
        financial_source_rate = float(data['financial_source_rate']) # نرخ خرید پول
        company_gain_rate = float(data['company_gain_rate']) # کارمزد توسعه
        investor_gain_rate = float(data['investor_gain_rate']) # کارمزد بازاریاب
        warranty_gain_rate = float(data['warranty_gain_rate']) # کارمزد صدور ضمانت نامه
        share_rate = float(data['share_rate']) # سهم توسعه از کارمزد صدور ضمانت نامه
        customer_check_factor = float(data['customer_check_factor'])
        surety_check_factor = float(data['surety_check_factor'])
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

        calc_out['complete_gain'] = calc_out['company_gain'] + calc_out['investor_gain'] + calc_out['warranty_gain'] * share_rate

        calc_out['loan_amount'] = calc_out['complete_gain'] + calc_out['supplier_balance'] + additional_costs

        calc_out['instalment_amount'] = calc_out['loan_amount'] * source * rate / (rate - 1)
        temp = int(round(calc_out['instalment_amount'] , -4))
        if temp - calc_out['instalment_amount'] < -1000:
            calc_out['instalment_amount'] = temp + 5000
        else:
            calc_out['instalment_amount'] = temp

        calc_out['total_amount_of_instalments'] = calc_out['instalment_amount'] * number_of_instalment

        calc_out['customer_check'] = int(round(calc_out['total_amount_of_instalments'] * customer_check_factor , -6)) + 1000000

        calc_out['surety_check'] = int(round(calc_out['total_amount_of_instalments']  * surety_check_factor , -6)) + 1000000

        calc_out['coffer_difference'] = int(net_amount - calc_out['downpayment'] - 
        calc_out['loan_amount'])

        calc_out['total_amount'] = int(calc_out['instalment_amount'] * number_of_instalment + 
        calc_out['downpayment'])

        calc_out['warranty_gain_share'] = int(calc_out['warranty_gain'] * share_rate)

        calc_out['initial_coffer_gain'] = int(calc_out['coffer_difference'] - calc_out['warranty_gain_share'])

        calc_out['facility'] = calc_out['loan_face_value'] - calc_out['initial_coffer_gain']

        calc_out['pure_company_gain'] = int( calc_out['company_gain'] + calc_out['warranty_gain_share'] )

        calc_out['total_company_gain'] = int(calc_out['company_gain'] + calc_out['investor_gain'] + calc_out['warranty_gain_share'] )

        calc_out['facility_rate'] = int(round( 100.0 * (number_of_instalment /12 )* 
        ( (calc_out['total_amount_of_instalments'] - (net_amount - calc_out['downpayment']) ) / 
        (net_amount - calc_out['downpayment']) ) ))
        
        ex = openpyxl.load_workbook(os.path.join(settings.BASE_DIR, 'contract_docs/input/calc.xlsx'))
        sheet = ex['Sheet1']
        sheet['A4'] = net_amount
        sheet['C4'] = discount
        sheet['A6'] =downpayment_rate
        sheet['A8'] = calc_out['downpayment']
        sheet['A10'] = number_of_instalment
        sheet['B6'] = warranty_gain_rate
        sheet['B4'] = financial_source_rate
        sheet['B8'] =share_rate
        sheet['B10'] = company_gain_rate
        sheet['B12'] =investor_gain_rate
        sheet['C6'] = customer_check_factor
        sheet['C8'] = surety_check_factor
        sheet['F2'] = calc_out['instalment_amount']
        sheet['F3'] = calc_out['total_amount_of_instalments']
        sheet['F4'] = calc_out['loan_amount']
        sheet['F5'] = calc_out['loan_face_value']
        sheet['F6'] = calc_out['company_gain']
        sheet['F7'] = calc_out['warranty_gain']
        sheet['F8'] = calc_out['pure_company_gain']
        sheet['F9'] = calc_out['investor_gain']
        sheet['F10'] = calc_out['total_company_gain'] + calc_out['supplier_balance']
        sheet['F11'] = calc_out['supplier_balance']
        sheet['F13'] = calc_out['customer_check']
        sheet['F14'] = calc_out['surety_check']
        path = os.path.join(OUTPUT_DIR , 'calcc.xlsx')
        ex.save(path)
    return JsonResponse(calc_out)

def download_excell(request):
    doc_destination = os.path.join(OUTPUT_DIR, 'calcc.xlsx')
    return FileResponse(open(doc_destination, 'rb'), as_attachment=True)

import numpy as np

class main_calculation:
    def __init__(self,input):
        self.in_dict = input
        self.output = self.calc()
        # self.calc_out = {}
    def calc(self):
        calc_out ={}
        data = self.in_dict
        # data.get('net_amount',0)
        net_amount = int(data['net_amount']) #مبلغ فاکتور
        face_net_amount = data.get('face_net_amount',net_amount)
        number_of_instalment = int(data.get('number_of_instalment',12)) #تعداد اقساط
        additional_costs = int(data['additional_costs']) #هزینه های اضافی
        downpayment_rate = float(data['downpayment_rate']) #(نسبت پیش پرداخت (بین ۰-۱
        discount = float(data['discount']) # تخفیف
        financial_source_rate = float(data['financial_source_rate']) # نرخ خرید پول
        company_gain_rate = float(data['company_gain_rate']) # کارمزد توسعه
        investor_gain_rate = float(data['investor_gain_rate']) # کارمزد بازاریاب
        warranty_gain_rate = float(data['warranty_gain_rate']) # کارمزد صدور ضمانت نامه
        share_rate = float(data['share_rate']) # سهم توسعه از کارمزد صدور ضمانت نامه
        nokol_rate = float(data.get('nokol_rate',0)) #کارمزد ذخیره تکول
        finance_gain_rate = float(data.get('finance_gain_rate',0)) #کارمزد تامین مالی
        issuer_type = data.get('issuer_type','0')
        customer_check_factor = float(data.get('customer_check_factor',1.1))
        surety_check_factor = float(data.get('surety_check_factor',1.5))
        sign_date = data.get('sign_date')
        duration = int(data.get('duration',0))
        num_of_pay = int(data.get('num_of_pay',0))
        suretys = data.get('suretys')
        loan_level = data.get('loan_level')
        calc_out['gradual_warranty_rate'] = 0
        calc_out['once_warranty_rate'] = 0
        if issuer_type == '1':
            calc_out['gradual_warranty_rate'] = warranty_gain_rate
        else:
            calc_out['once_warranty_rate'] = warranty_gain_rate
        if sign_date is not None:
            calc_out['check_dates'] = []
            pdate = jalali.Gregorian(sign_date).persian_tuple()
            persian_date_format = '{}/{}/{}'
            for i in NUMBER_PAY_DICT[duration][1][num_of_pay]:
                year,month,day = pdate
                month  += i
                if month > 12:
                    month -= 12
                    year += 1
                if month==12 and day > 28:
                    day = 28
                calc_out['check_dates'].append(persian_date_format.format(year,month,day))
        else:
            calc_out['check_dates'] = []
        calc_out['discounted_net_amount'] = int(round(net_amount - face_net_amount * discount , -4)) #مبلغ فاکتور پس از تخفیف

        calc_out['downpayment'] = int(round(net_amount * downpayment_rate , -4)) # پیش پرداخت

        calc_out['loan_face_value'] = net_amount - calc_out['downpayment']

        calc_out['supplier_balance'] = int(round(calc_out['discounted_net_amount'] - calc_out['downpayment'] , -4)) #تسویه ی فروشگاه

        calc_out['company_gain'] = int(round(face_net_amount * company_gain_rate))
        
        calc_out['investor_gain'] = int(round(face_net_amount * investor_gain_rate))
        
        calc_out['initial_facility'] = int((calc_out['supplier_balance'] +calc_out['company_gain'] + calc_out['investor_gain']) 
                                           / (1 - nokol_rate - finance_gain_rate - calc_out['once_warranty_rate']))
        if num_of_pay != 0 and duration != 0:
            inst_interval = duration / num_of_pay
            correction =  0.0118*inst_interval**2 + 0.975*inst_interval + 0.0094
            correct_finance_gain_rate = financial_source_rate / 12 * correction * 1.01
            calc_out['correction'] = correction
            calc_out['correct_finance_gain_rate'] = correct_finance_gain_rate
            calc_out['duration_inst'] = pmt(correct_finance_gain_rate,num_of_pay,-calc_out['initial_facility'])
            temp = int(round(calc_out['duration_inst'] , -4))
            if temp - calc_out['duration_inst'] < -1000:
                calc_out['duration_inst'] = temp + 5000
            else:
                calc_out['duration_inst'] = temp
            calc_out['duration_total_inst'] = calc_out['duration_inst'] * num_of_pay
            calc_out['duration_total_amount'] = calc_out['duration_total_inst'] + calc_out['downpayment']
        else:
            calc_out['duration_inst'] = 0
            calc_out['duration_total_inst'] = 0
            calc_out['duration_total_amount'] = 0 
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

        calc_out['customer_check'] = int(round(calc_out['total_amount_of_instalments'] * customer_check_factor , -6)) + 1000000

        calc_out['surety_check'] = int(round(calc_out['total_amount_of_instalments']  * surety_check_factor , -6)) + 1000000

        calc_out['coffer_difference'] = int(net_amount - calc_out['downpayment'] - calc_out['loan_amount'])

        calc_out['total_amount'] = int(calc_out['instalment_amount'] * number_of_instalment + calc_out['downpayment'])

        calc_out['warranty_gain_share'] = int(calc_out['warranty_gain'] * share_rate)

        calc_out['initial_coffer_gain'] = int(calc_out['coffer_difference'] - calc_out['warranty_gain_share'])

        calc_out['facility'] = calc_out['loan_face_value'] - calc_out['initial_coffer_gain']
        if loan_level != None and suretys != None:
            if calc_out['loan_face_value'] <= loan_level['1']:
                calc_out['level'] = '1'
                calc_out['level_str'] = 'سطح ۱'
                calc_out['suretys'] = suretys['1']
            elif calc_out['loan_face_value'] <= loan_level['2']:
                calc_out['level'] = '2'
                calc_out['level_str'] = 'سطح ۲'
                calc_out['suretys'] = suretys['2']
            elif calc_out['loan_face_value'] <= loan_level['3']:
                calc_out['level'] = '3'
                calc_out['level_str'] = 'سطح ۳'
                calc_out['suretys'] = suretys['3']
            elif calc_out['loan_face_value'] <= loan_level['4']:
                calc_out['level'] = '4'
                calc_out['level_str'] = 'سطح ۴'
                calc_out['suretys'] = suretys['4']

        calc_out['pure_company_gain'] = int( calc_out['company_gain'] + calc_out['warranty_gain_share'] )

        calc_out['total_company_gain'] = int(calc_out['company_gain'] + calc_out['investor_gain'] + calc_out['warranty_gain_share'] )
        if net_amount - calc_out['downpayment'] > 0:
            calc_out['facility_rate'] = int(round( 100.0 * (number_of_instalment /12 )* 
            ( (calc_out['total_amount_of_instalments'] - (net_amount - calc_out['downpayment']) ) / 
            (net_amount - calc_out['downpayment']) ) ))
        else:
            calc_out['facility_rate'] = 0
        return calc_out
    def admin(self):
        li = (
        "discounted_net_amount",
        "downpayment",
        "loan_face_value",
        "supplier_balance",
        "company_gain",
        "investor_gain",
        "warranty_gain",
        "complete_gain",
        "loan_amount",
        "instalment_amount",
        "total_amount_of_instalments",
        "customer_check",
        "surety_check",
        "coffer_difference" ,
        "total_amount" ,
        "warranty_gain_share" ,
        "initial_coffer_gain",
        "facility" ,
        "pure_company_gain" ,
        "total_company_gain" ,
        "facility_rate",
        "check_dates",
        "duration_inst",
        "duration_total_inst",
        "duration_total_amount"
        )
        
        data = dict((k, self.output[k]) for k in li)
        if data["duration_inst"] != 0:
            data['instalment_amount'] = data["duration_inst"]
            data['total_amount_of_instalments'] = data['duration_total_inst']
            data['total_amount'] = data['duration_total_amount']
        else:
            pass
        return data
    def customer(self):
        li = ("discounted_net_amount",
        "downpayment",
        "loan_face_value",
        "level",
        "level_str",
        "suretys",
        "supplier_balance",
        "company_gain",
        "investor_gain",
        "warranty_gain",
        "complete_gain",
        "loan_amount",
        "instalment_amount",
        "total_amount_of_instalments",
        "customer_check",
        "surety_check",
        "total_amount",)
        return dict((k, self.output[k]) for k in li)
    def supp(self):
        lii = ("downpayment",
        "duration_inst",
        "duration_total_inst",
        "duration_total_amount",
        "check_dates",
        'initial_facility',
        'correction',
        'correct_finance_gain_rate')
        
        data = dict((k, self.output[k]) for k in lii)
        data['instalment_amount'] = data["duration_inst"]
        data['total_amount_of_instalments'] = data['duration_total_inst']
        data['total_amount'] = data['duration_total_amount']
        return data
    def supplier(self):
        li = (
        "discounted_net_amount",
        "downpayment",
        "loan_face_value",
        "supplier_balance",
        "company_gain",
        "investor_gain",
        "warranty_gain",
        "complete_gain",
        "loan_amount",
        "instalment_amount",
        "total_amount_of_instalments",
        "customer_check",
        "surety_check",
        "total_amount"
        )
        
        return dict((k, self.output[k]) for k in li)



@api_view(['POST'])
@permission_classes([])
@schema(AutoSchema())
def calculator(request):
    calc_out = {}
    if request.method == 'POST':
        data = json.loads(request.body)
        net_amount = int(data['net_amount']) #مبلغ فاکتور
        number_of_instalment = int(data['number_of_instalment']) #تعداد اقساط
        additional_costs = int(data['additional_costs']) #هزینه های اضافی
        downpayment_rate = float(data['downpayment_rate']) #(نسبت پیش پرداخت (بین ۰-۱
        discount = float(data['discount']) # تخفیف
        financial_source_rate = float(data['financial_source_rate']) # نرخ خرید پول
        company_gain_rate = float(data['company_gain_rate']) # کارمزد توسعه
        investor_gain_rate = float(data['investor_gain_rate']) # کارمزد بازاریاب
        warranty_gain_rate = float(data['warranty_gain_rate']) # کارمزد صدور ضمانت نامه
        share_rate = float(data['share_rate']) # سهم توسعه از کارمزد صدور ضمانت نامه
        customer_check_factor = float(data['customer_check_factor'])
        surety_check_factor = float(data['surety_check_factor'])
        
        my_calc = main_calculation(data)
        calc_out = my_calc.admin()
        ex = openpyxl.load_workbook(os.path.join(settings.BASE_DIR, 'contract_docs/input/calc.xlsx'))
        sheet = ex['Sheet1']
        sheet['A4'] = net_amount
        sheet['C4'] = discount
        sheet['A6'] =downpayment_rate
        sheet['A8'] = calc_out['downpayment']
        sheet['A10'] = number_of_instalment
        sheet['B6'] = warranty_gain_rate
        sheet['B4'] = financial_source_rate
        sheet['B8'] =share_rate
        sheet['B10'] = company_gain_rate
        sheet['B12'] =investor_gain_rate
        sheet['C6'] = customer_check_factor
        sheet['C8'] = surety_check_factor
        sheet['F2'] = calc_out['instalment_amount']
        sheet['F3'] = calc_out['total_amount_of_instalments']
        sheet['F4'] = calc_out['loan_amount']
        sheet['F5'] = calc_out['loan_face_value']
        sheet['F6'] = calc_out['company_gain']
        sheet['F7'] = calc_out['warranty_gain']
        sheet['F8'] = calc_out['pure_company_gain']
        sheet['F9'] = calc_out['investor_gain']
        sheet['F10'] = calc_out['total_company_gain'] + calc_out['supplier_balance']
        sheet['F11'] = calc_out['supplier_balance']
        sheet['F13'] = calc_out['customer_check']
        sheet['F14'] = calc_out['surety_check']
        path = os.path.join(OUTPUT_DIR,'calcc.xlsx')
        ex.save(path)
    return JsonResponse(calc_out)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class TokenObtainser_supp(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': _('نام کاربر یافت نشد') ,
        'no_supp': _('تامین کننده یافت نشد')
    }
    def validate(self, attrs):
        data = super().validate(attrs)

        try:
            supplier.objects.get(user=self.user)
            return data
        except:
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_supp'],
                'no_supp',
            )
class TokenObtainser_cust(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': _('نام کاربر یافت نشد') ,
        'no_cust': _('متقاضی یافت نشد')
    }
    def validate(self, attrs):
        data = super().validate(attrs)

        try:
            customer.objects.get(user=self.user)
            return data
        except:
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_cust'],
                'no_cust',
            )
            

        
    
class TokenObtainPair_supp(TokenObtainPairView):
    serializer_class = TokenObtainser_supp
class TokenObtainPair_cust(TokenObtainPairView):
    serializer_class = TokenObtainser_cust
