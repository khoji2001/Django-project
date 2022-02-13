import os
from users.views import main_calculation
from django.conf import settings
from mailmerge import MailMerge
from datetime import date
from django.core.mail import EmailMessage
from OTP.models import select_MessageText
from django.contrib.postgres.fields import ArrayField
from customer.models import Guarantee, LEVEL_DICT , JOB_CLASSES_DICT
from django.db import models
from django.db.models import Sum,Max,F,Case,When
from extensions import jalali
from extensions.utill import persian_numbers_converter,convert,convert_to_englishnum
from django.utils import timezone
from datetime import timedelta
from django.utils.functional import cached_property
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import jdatetime
import pytz
from OTP.views import send_sms
from config.settings import ADMIN_EMAILS
import datetime
from OTP.models import Emails

# Create your models here.
VCC_STATUSES = (
    ('0' , 'آزاد'),
    ('1' ,'مصرف شده'),
    ('2' , 'در حال استفاده'),
)
NEW_STATUS = (
    ('0' , 'نامعلوم'),
    ('1' ,'بخشوده'),
    ('2' , 'پرداخت'),
)
def add_card(vcc_number):
    try:
        vcc.objects.get(number = vcc_number)
    except ObjectDoesNotExist:
        Vcc = vcc(number = vcc_number)
        Vcc.save()

class Vcc(models.Model):
    number = models.CharField (max_length = 16 , unique = True , verbose_name = 'شماره کارت')
    amount = models.IntegerField(default = 0 , verbose_name = 'موجودی')
    status = models.CharField(max_length = 1 ,default = '0'  ,choices = VCC_STATUSES, verbose_name = 'وضعیت')
    instalment_amount = models.IntegerField(default = 0 , verbose_name = 'مبلغ قسط')
    coffer = models.ForeignKey('supplier.coffer', on_delete = models.SET_NULL , blank=True,null = True, verbose_name = 'تامین کننده مالی')
    new_status = models.CharField(max_length = 1 ,default = '0'  ,choices = NEW_STATUS, verbose_name = ' وضعیت پرداخت جریمه')
    startt = ArrayField(models.IntegerField(null=True, blank=True), blank=True,null = True, verbose_name = 'روز سررسید')
    class Meta:
        verbose_name = 'کارت بانکی'
        verbose_name_plural = 'وصول مطالبات'

    def save(self, *args , **kwargs):
        self.number = convert_to_englishnum(self.number)
        if self.status == '0':
            queryset = payment.objects.filter(VCC = self)
            for p in queryset:
                p.VCC = None
                p.save()
            self.amount = 0
            self.instalment_amount = 0
        try: 
            c = self.contract
            self.status = '2'
            self.instalment_amount = c.instalment_amount
        except:
            pass
        
        try:
            x = str(self.contract.jjinstalment_start_date)
            x = x.split('-')
            x = [int(x[0]),int(x[1]),int(x[2]),]
            self.startt = x
            
        except:
            
            self.startt = [1300,1,1]
        
        super(vcc,self).save(*args,**kwargs)

    def pamount(self):
        return persian_numbers_converter(self.amount , 'price')
    pamount.short_description = 'موجودی'
    pamount.admin_order_field = 'amount'  
    def __str__(self):
        return self.number
class CardManager_free(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='0')
class CardManager_nok(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(contract__status='6')
class CardManager_busy(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status__in=['1','2'])
class Nok_vcc(vcc):
    objects = CardManager_nok()
    class Meta:
        proxy = True
        verbose_name = 'پرونده نکول شده'
        verbose_name_plural = 'پرونده های نکول شده'
class Vcc_free(vcc):
    objects = CardManager_free()
    class Meta:
        proxy = True
        verbose_name = 'کارت بانکی آزاد'
        verbose_name_plural = 'کارت های بانکی آزاد'
class Vcc_busy(vcc):
    objects = CardManager_busy()
    class Meta:
        proxy = True
        verbose_name = 'وصول مطالبه'
        verbose_name_plural = 'وصول مطالبات'

class Due_contractsManager(models.Manager):
    def get_queryset(self):
        now = timezone.now().date()
        year,month,today = jalali.Gregorian(now).persian_tuple()
        if month < 7:
            month_days = 31
        elif month < 12:
            month_days = 30
        elif month == 12:
            month_days = 29
        dued_contracts = []
        temp_contracts = super().get_queryset().filter(status__in = ['2','3','4'])
        for c in temp_contracts:
            try:
                start_date = c.start_date_ins
                c_dueday = jalali.Gregorian(start_date).persian_tuple()[2]
                if today == (c_dueday - 2) % month_days + 1 and now >= start_date - timedelta(days= 3) and now < start_date + timedelta(days= int(c.number_of_instalment/12 * 365)):
                    dued_contracts.append(c)
            except:
                pass
        return dued_contracts

class Debt_contractsManager(models.Manager):
    def get_queryset(self):
        debt_contracts = []
        temp_contracts = super().get_queryset().filter(status = '4')
        for c in temp_contracts:
            if c.old_debit_amount() > 500000:
                debt_contracts.append(c)
        return debt_contracts

class Clear_contractsManager(models.Manager):
    def get_queryset(self):
        clear_contracts = []
        temp_contracts = super().get_queryset().filter(status = '4').annotate(
            customer_mellicode = F('customer__user__melli_code'),
            last_pay_date = Max('payments__date')
        )
        for c in temp_contracts:
            if c.remaining_amount() <= 0:
                clear_contracts.append(c)
        return clear_contracts
LOAN_LEVEL = CUSTOMER_LEVEL = {
    '0' : 0,
    '1' : 120000000,
    '2' : 150000000,
    '3' : 300000000
}
CONTRACT_STATUSES = (
        ('0' , 'تایید دریافت پیش پرداخت'),
        ('1' , 'درحال عقد قرارداد'),
        ('2' , ' تایید قرارداد و ارسال کالا'),
        ('3' , 'تسویه با فروشگاه'),
        ('4' , 'پرداخت اقساط توسط متقاضی'),
        ('5' , 'تسویه متقاضی و تحویل مدارک'),
        ('6' , 'نکول قطعی'),
        ('7' , 'انصراف متقاضی'),
        )
SEND_TO_COFFER_STATUSES = (
    (True , 'ارسال شده'),
    (False , 'ارسال نشده')
)
TYPE_CHOICES = (
        ('0' , 'نوع ۱( محاسبات طبق اکسل)') , 
        ('1' , 'نوع ۲(محاسبات irr)') ,
    )
PAY_STATUS_DICT = {
    '1' : 'خوش حساب',
    '2' : 'پرداخت نامنظم',
    '3' : 'پرداخت پرخطر',
    '4' : 'بدحساب'
}
def validate_rate(value):
    if value < 0 or value > 1:
        raise ValidationError(
            _('%(value)s بین ۰-۱ نیست.'),
            params={'value': value},
        )
class Contract(models.Model):
    customer = models.ForeignKey('customer.customer', on_delete = models.SET_NULL , null = True, verbose_name = 'متقاضی')
    supplier = models.ForeignKey('supplier.supplier', on_delete = models.SET_NULL , null = True, verbose_name = 'تأمین کننده')
    Type = models.CharField(max_length = 1 , default = '1' ,choices = TYPE_CHOICES , verbose_name = "نوع قرارداد" )
    vcc = models.OneToOneField(vcc, on_delete = models.SET_NULL , null = True,blank = True , verbose_name = ' کارت مجازی')
    sign_date = models.DateField(editable = True, blank = True , null = True , verbose_name = 'تاریخ امضا' )
    start_date_ins = models.DateField(editable = True, blank = True , null = True , verbose_name = 'تاریخ شروع اقساط' )
    invoice_date = models.DateField(editable = True, blank = True , null = True , verbose_name = 'تاریخ فاکتور')
    invoice_number = models.CharField(max_length = 20 ,default = '' ,blank = True, verbose_name = 'شماره فاکتور')
    description = models.TextField(verbose_name = 'شرح فاکتور' ,default = '', blank = True)
    clearing_date = models.DateField(editable = True, blank = True , null = True , verbose_name = 'تاریخ تسویه با فروشگاه' )
    net_amount = models.PositiveIntegerField( verbose_name = 'مبلغ فاکتور' , help_text = 'ریال')
    face_net_amount = models.PositiveIntegerField( verbose_name = 'مبلغ فاکتور ظاهری' , help_text = 'ریال',blank=True)
    number_of_instalment = models.IntegerField( default = 12 , verbose_name = 'تعداد اقساط' )
    additional_costs = models.IntegerField( blank = True , verbose_name = 'هزینه ی اضافی' , help_text = 'ریال')
    downpayment = models.IntegerField( blank = True , verbose_name = 'پیش پرداخت' , help_text = 'ریال')
    status = models.CharField(max_length = 2,default = '0'  ,choices = CONTRACT_STATUSES, verbose_name = 'وضعیت قراردادی')
    send_to_coffer = models.BooleanField(default=False , choices=SEND_TO_COFFER_STATUSES,verbose_name='وضعیت ارسال به تامین مالی')
    customer_fullname = models.CharField(max_length = 50, default = '' , verbose_name = 'نام کامل متقاضی')
    supplier_name = models.CharField(max_length = 50, default = '' , verbose_name = 'نام فروشگاه')
    contract_id = models.CharField(max_length = 20 , unique = True ,blank=True, null = True, verbose_name = 'شماره قرارداد')
    financial_source_rate = models.FloatField( blank =True , verbose_name = 'نرخ تسهیلات', validators = [validate_rate])
    warranty_gain_rate = models.FloatField( blank =True , verbose_name = 'کارمزد صدور ضمانت نامه', validators = [validate_rate])
    share_rate = models.FloatField( blank =True , verbose_name = '  سهم شرکت از ضمانت نامه', validators = [validate_rate])
    company_gain_rate = models.FloatField( blank = True ,verbose_name = 'کارمزد شرکت' , validators = [validate_rate])
    investor_gain_rate = models.FloatField( blank = True ,verbose_name = 'کارمزد بازاریاب', validators = [validate_rate] )
    discount = models.FloatField(blank = True ,verbose_name = 'تخفیف' , validators = [validate_rate])
    customer_check_factor = models.FloatField(default=1.1 , verbose_name='ضریب چک متقاضی')
    surety_check_factor = models.FloatField(default=1.5 , verbose_name='ضریب چک ضامن')
    vcc_number =  models.CharField (max_length = 16 , default = '', verbose_name = 'شماره کارت')
    pay_day= models.PositiveSmallIntegerField( default =0 ,verbose_name = 'روز پرداخت قسط' )
    appoint_time = models.DateTimeField(blank = True , null = True ,unique = True, verbose_name= " زمان قرارملاقات")
    contract_permission_date = models.DateField(verbose_name='تاریخ صدور مجوز قرارداد', null=True, blank=True)
    coffer = models.ForeignKey('supplier.coffer', on_delete = models.SET_NULL , null = True, verbose_name = 'تامین کننده مالی',blank = True)
    issuer = models.ForeignKey('supplier.issuer', on_delete = models.SET_NULL , null = True, verbose_name = 'صادر کننده ضمانت نامه',blank = True)
    amount_of_installment = models.PositiveIntegerField( blank = True, null = True, verbose_name = 'مبلغ قسط' , help_text = 'ریال')

    objects = models.Manager()
    due_contracts = due_contractsManager()
    debt_contracts = debt_contractsManager()
    clear_contracts = clear_contractsManager()

    class Meta:
        verbose_name = 'قرارداد'
        verbose_name_plural = 'قراردادها'
        permissions = [
            ("افراد حقوقی", "وصول مطالبات نکول شده و قرارداد های ارسال شده"),
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_status = self.status
        self.original_sign_date = self.sign_date
        if self.start_date_ins is not None:
            self.instalment_start_date = self.start_date_ins
        else:
            self.instalment_start_date = self.instalment_start_datee()
        if self.pk != None:
            data ={}
            data['net_amount'] = self.net_amount
            data['face_net_amount'] = self.face_net_amount
            data['number_of_instalment'] = self.number_of_instalment
            data['additional_costs'] = self.additional_costs
            data['downpayment_rate'] = self.downpayment / self.net_amount
            data['discount'] = self.discount
            data['financial_source_rate'] = self.financial_source_rate
            data['company_gain_rate'] = self.company_gain_rate  
            data['investor_gain_rate'] = self.investor_gain_rate
            data['warranty_gain_rate'] = self.warranty_gain_rate
            data['share_rate'] = self.share_rate
            data['customer_check_factor'] = float(self.customer_check_factor)
            data['surety_check_factor'] = float(self.surety_check_factor)
            my_calc = main_calculation(data)
            x = my_calc.admin()

            self.discounted_net_amount = x['discounted_net_amount']
            self.loan_face_value = x['loan_face_value']
            self.supplier_balance = x['supplier_balance']
            self.company_gain = x['company_gain']
            self.investor_gain = x['investor_gain']
            
            if self.Type == '0':
                self.warranty_gain =  int(round( self.instalment_rate * self.warranty_gain_rate * (self.company_gain + self.investor_gain + self.supplier_balance) / (1-(self.instalment_rate * self.warranty_gain_rate )) ))
            elif(self.Type == '1'):
                self.warranty_gain = x['warranty_gain']   

            self.complete_gain = x['complete_gain']
            self.loan_amount = x['loan_amount']
            if (self.Type == '1'):
                self.instalment_amount = x['instalment_amount']
            elif (self.Type == '0'):
                temp =  self.loan_amount * self.instalment_rate / self.number_of_instalment
                rounded_temp = int(round(temp , -4))
                if rounded_temp - temp <-1000:
                    self.instalment_amount =  rounded_temp + 5000
                else:
                    self.instalment_amount = rounded_temp
            if self.status in ['2','3','4','5','6'] and self.amount_of_installment != None:
                self.instalment_amount = self.amount_of_installment
            self.customer_check = x['customer_check']
            self.surety_check = x['surety_check']
            self.coffer_difference = x['coffer_difference']
            self.total_amount_of_instalments = self.instalment_amount * self.number_of_instalment
            self.total_amount = self.total_amount_of_instalments + self.downpayment
            self.warranty_gain_share = x['warranty_gain_share']
            self.initial_coffer_gain = x['initial_coffer_gain']
            self.facility = x['facility']
            self.pure_company_gain = x['pure_company_gain']
            self.total_company_gain = x['total_company_gain']
            self.facility_rate = x['facility_rate']

    def get_dueconts(date):
        now = timezone.now().date()
        year,month,today = jalali.Gregorian(date).persian_tuple()
        if month < 7:
            month_days = 31
        elif month < 12:
            month_days = 30
        elif month == 12:
            month_days = 29
        dued_contracts = []
        temp_contracts = contract.objects.filter(status__in = ['2','3','4'])
        for c in temp_contracts:
            try:
                start_date = c.start_date_ins
                c_dueday = jalali.Gregorian(start_date).persian_tuple()[2]
                if (today == (c_dueday - 2) % month_days + 1 and now >= start_date - timedelta(days= 3)):
                    dued_contracts.append(c)
            except:
                pass
        return dued_contracts
    def date(self):
        return persian_numbers_converter(jdatetime.date.fromgregorian(date = self.appoint_time.date(),locale = "fa_IR").strftime("%a, %d %b %Y"))
    def time(self):
        return persian_numbers_converter(self.appoint_time.astimezone(pytz.timezone('Asia/Tehran')).time())[:-3]
    @cached_property
    def instalment_rate(self):
        if self.number_of_instalment <= 12:
            return 1 + self.financial_source_rate * 0.5648
        else:
            return 1 + self.financial_source_rate * 1.1362

    def clean(self):
        if self.customer.level == '0':
            raise ValidationError("سطح تسهیلات متقاضی تعیین نشده است")	
    
    
    @property
    def instalment_due_day(self):
        temp_date = jalali.Gregorian(self.start_date_ins).persian_tuple()
        return persian_numbers_converter(temp_date[2])

    
    @property
    def instalment_amount_persian(self):
        return persian_numbers_converter(self.instalment_amount , 'price')

    @property
    def total_amount_of_instalments_persian(self):
        return persian_numbers_converter(self.total_amount_of_instalments , 'price')

    @staticmethod
    def calc_delay_coe(delay_days):
        delay_coe = delay_days // 2
        if delay_coe > 5:
            delay_coe = 5
        elif delay_coe == 4:
            delay_coe = 3
        return delay_coe
    @cached_property
    def instalment_detail(self):
        penalty_rate = 0.001
        try:
            pays = self.payments.all().order_by('date')
            instalment_date = self.start_date_ins
            delay_penalty = 0
            acceleration_award = 0
            penalty = 0
            total_difference = 0
            pay_pointer = 0
            last_difference = 0
            if len(pays) > 0:
                current_due = last_due = pays[0].date if pays[0].date < instalment_date else instalment_date
            else:
                current_due = last_due = instalment_date
                
            while instalment_date <= timezone.now().date():
                last_due = current_due
                temp = jalali.Gregorian(instalment_date).persian_tuple()
                #compute delta time for monday of next work week from signdate
                if temp[1] < 7: #first half of year
                    delta_2 = timedelta(days=31)
                elif temp[1] == 12: #esfand month
                    if temp[0] % 4 == 0 or temp[0] == 1399: #kabise year
                        delta_2 = timedelta(days=30)
                    else: #not kabise
                        delta_2 = timedelta(days=29)
                else: #second half of year and not esfand
                    delta_2 = timedelta(days=30)
                try:
                    current_pay = pays[pay_pointer]
                    if current_pay.date < instalment_date:
                        current_due = current_pay.date
                        flag = False
                    else:
                        raise Exception
                except:
                    current_due = instalment_date
                    flag = True
                delay_days = (current_due - last_due).days
                delay_coe = self.calc_delay_coe(delay_days)
                if last_difference > 0:
                    penalty += last_difference * penalty_rate * delay_days
                    delay_penalty += last_difference * delay_days // 30 * delay_coe
                else:
                    acceleration_award += -last_difference * delay_days // 30
                if flag:
                    last_difference += self.instalment_amount
                    instalment_date += delta_2
                else:
                    last_difference -= current_pay.amount
                    pay_pointer += 1

            total_difference = delay_penalty - acceleration_award
            if total_difference < self.instalment_amount * (self.number_of_instalment / 12):
                pay_status = '1'
            elif total_difference < self.instalment_amount * (self.number_of_instalment / 5):
                pay_status = '2'
            elif total_difference < self.instalment_amount * (self.number_of_instalment / 3):
                pay_status = '3'
            else:
                pay_status = '4'
            return (int(penalty),pay_status)
        except Exception as e:
            print(str(e))

    def remaining_amount(self):
        if self.status == '5' or self.status == '7':
            return 0
        try:
            return self.total_amount_of_instalments - self.vcc.amount
        except Exception as e:
            return self.total_amount_of_instalments
    remaining_amount.short_description = 'مبلغ باقی مانده'

    def old_debit_amount(self):
        if self.status == '4':
            year_1,month_1,day_1 = jalali.Gregorian(timezone.now().date()).persian_tuple()
            year_2,month_2,day_2= jalali.Gregorian(self.start_date_ins).persian_tuple()
            months = (year_1 - year_2)*12 + month_1 - month_2
            if day_1 > day_2:
                months += 1
            if months<0:
                months = 0
            if months>self.number_of_instalment:
                months = self.number_of_instalment
            try:
                face_pay_value = months * self.instalment_amount
                return face_pay_value - self.vcc.amount
            except:
                return 0
        else:
            return 0
    @property
    def old_debit_amount_persian(self):
        return persian_numbers_converter(self.old_debit_amount() , 'price')

    @property
    def old_debit_amount_persian(self):
        return persian_numbers_converter(self.old_debit_amount() , 'price')

    def debit_amount(self):
        if self.status in ['4','6']:
            try:
                year_1,month_1,day_1 = jalali.Gregorian(timezone.now().date()).persian_tuple()
                year_2,month_2,day_2= jalali.Gregorian(self.start_date_ins).persian_tuple()
                months = (year_1 - year_2)*12 + month_1 - month_2
                if day_1 >= day_2:
                    months += 1
                if months<0:
                    months = 0
                if months>self.number_of_instalment:
                    months = self.number_of_instalment
                try:
                    face_pay_value = months * self.instalment_amount
                    return face_pay_value - self.vcc.amount
                except:
                    return 0
            except:
                return 0
        else:
            return 0 
    debit_amount.short_description = 'مبلغ بدهی'

    @property
    def debit_amount_persian(self):
        return persian_numbers_converter(self.debit_amount() , 'price')
        
    def number_of_pays(self):
        return payment.objects.filter(contract = self).count()
    number_of_pays.short_description = 'تعداد واریزها'

    def pnet_amount(self):
        return self.net_amount_persian
    pnet_amount.short_description = 'مبلغ فاکتور'

    def ptotal_amount_of_instalments(self):
        return self.total_amount_of_instalments_persian
    ptotal_amount_of_instalments.short_description = 'مجموع اقساط'

    def ploan_amount(self):
        return self.loan_amount_persian
    ploan_amount.short_description = 'تسهیلات'

    def ploan_face_value(self):
        return persian_numbers_converter(self.loan_face_value , 'price')
    ploan_face_value.short_description = 'عدد ظاهری وام'

    def pinstalment_amount(self):
        return self.instalment_amount_persian
    pinstalment_amount.short_description = 'مبلغ هر قسط'

    def pnumber_of_instalment(self):
        return self.number_of_instalment_persian
    pnumber_of_instalment.short_description = 'تعداد اقساط'

    def pdownpayment(self):
        return self.downpayment_persian
    pdownpayment.short_description = 'پیش پرداخت'

    def pinitial_coffer_gain(self):
        return persian_numbers_converter(self.initial_coffer_gain , 'price')
    pinitial_coffer_gain.short_description = 'کارمزد ابتدای کار تامین مالی'

    def psupplier_balance(self):
        return persian_numbers_converter(self.supplier_balance , 'price')
    psupplier_balance.short_description = 'تسویه فروشگاه'

    def pdiscount(self):
        return persian_numbers_converter(int(self.discount * 100))
    pdiscount.short_description = 'تخفیف'

    def pcompany_gain(self):
        return persian_numbers_converter(self.company_gain , 'price')
    pcompany_gain.short_description = 'کارمزد طرح از فاکتور'

    def pinvestor_gain(self):
        return persian_numbers_converter( self.investor_gain , 'price' )
    pinvestor_gain.short_description = 'کارمزد بازاریاب'

    def pwarranty_gain(self):
        return persian_numbers_converter( self.warranty_gain_share , 'price' )
    pwarranty_gain.short_description = 'کارمزد طرح از ضمانت نامه'

    def ptotal_company_gain(self):
        return persian_numbers_converter(self.total_company_gain , 'price')
    ptotal_company_gain.short_description = 'تسویه با طرح'

    def ptotal_amount(self):
        return self.total_amount_persian
    ptotal_amount.short_description = 'مبلغ کل اقساطی'
    def customer_mobile(self):
        return self.customer.mobile_number
    customer_mobile.short_description = 'شماره همراه'
    def No(self):
        try:
            No = int(self.contract_id.split('-')[1])
            return No + 1
        except:
            today_contracts = list(contract.objects.filter(sign_date = self.sign_date , supplier = self.supplier).order_by('contract_id'))
            if len(today_contracts) == 0:
                return 1
            else:
                for c in today_contracts[::-1]:
                    if c.id != self.id:
                        return c.No()
                return 1
    def save(self, *args , **kwargs):
        fac = {
            '1': 'max_fac1',
            '2': 'max_fac2',
            '3': 'max_fac3',
            '4':'max_fac4'
        }
        if self.original_sign_date != self.sign_date or (self.start_date_ins == None and self.sign_date != None):
            self.start_date_ins = self.instalment_start_datee()

        if self.status == '2'and self.original_status!=self.status and self.amount_of_installment is None:
            self.amount_of_installment = self.instalment_amount

        if self.status == '6' and self.original_status!=self.status:
            email_dict = {
                'customer' : self.customer.full_name(),
                'today' : jalali.Gregorian(date.today()).persian_string('{}-{}-{}'),
                'c_id' : self.contract_id,
                }
            try:
                email_dict['vcc_det'] = self.vcc.new_status
            except:
                email_dict['vcc_det'] = ''
            emaill = Emails.objects.get(email_type = '8')
            too = [x.strip() for x in emaill.TO.split(',')]
            number_debit = self.debit_amount()//self.instalment_amount
            
            document = MailMerge(os.path.join(settings.BASE_DIR,"contract_docs/input/nokol.docx"))
            context = {"date" : str(persian_numbers_converter(jalali.Gregorian(date.today()).persian_string('{}/{}/{}'))) ,
              "contract_id" :  str(self.contract_id),
              "customer_name" : f'{self.customer.first_name} {self.customer.last_name}' , 
              "customer_mobile" : str(persian_numbers_converter(self.customer.mobile_number)),
              "customer_phone" : str(persian_numbers_converter(self.customer.phone_number)),
              "instalment_amount" : str(persian_numbers_converter(self.instalment_amount,'price')),
              "start_date" : str(persian_numbers_converter(jalali.Gregorian(self.start_date_ins).persian_string('{}/{}/{}'))) ,
              "vcc_number" : str(self.vcc),
              "number_of_debit" : str(persian_numbers_converter(number_debit)),
            }
            document.merge(**context)
            destination = os.path.join(settings.BASE_DIR,f'contract_docs/نکول{self.contract_id}.docx')
            document.write(destination)
            document.close()

            
            pdf_dest = os.path.join(settings.BASE_DIR,'contract_docs/nokk')
            os.system ("libreoffice --headless --convert-to pdf --outdir "+pdf_dest + " "+ destination)
        
            email = EmailMessage(subject = emaill.ST.format(**email_dict),body = emaill.ET.format(**email_dict),from_email = 'admin@test.com', to = too ,headers= {'Content_Type' :'text/plain'})
            email.attach_file( os.path.join(settings.BASE_DIR,f'contract_docs/nokk/نکول{self.contract_id}.pdf'))
            email.send()
            os.remove(os.path.join(settings.BASE_DIR,f'contract_docs/nokk/نکول{self.contract_id}.pdf'))
            os.remove(destination)
            
        
        if self.status == '1':
            tdate =timezone.now()
            y = tdate.date()
            self.contract_permission_date = y
        if self.pk == None:
            self.issuer = self.supplier.issuer
            self.coffer = self.supplier.coffer
        if self.customer != None:
            self.customer_fullname = self.customer.user.get_full_name()
            if self.supplier != None:
                if self.pk == None:
                    if self.customer.level == '0':
                        raise ValidationError('سطح متقاضی تعیین نشده است'
                    )
                    else:
                        loan = getattr(self.supplier,fac[self.customer.level])
                    max_loan = 1000000 * loan // 0.75
                    
                    if self.net_amount < max_loan:
                        self.face_net_amount = self.net_amount
                    else:
                        self.face_net_amount = max_loan
                self.supplier.customer.add(self.customer)
                self.supplier_name = self.supplier.name
                if (self.discount == None):
                    self.discount = self.supplier.discount
                if (self.investor_gain_rate == None):
                    self.investor_gain_rate = self.supplier.investor_gain_rate
                if (self.company_gain_rate == None):
                    if self.number_of_instalment > 12:
                        self.company_gain_rate = self.supplier.company_gain_rate_two
                    else:
                        self.company_gain_rate = self.supplier.company_gain_rate_one
                if (self.financial_source_rate == None):
                    if self.number_of_instalment <= 12:
                        self.financial_source_rate = self.supplier.coffer.financial_source_rate1
                    else:
                        self.financial_source_rate = self.supplier.coffer.financial_source_rate2

                if (self.warranty_gain_rate == None):
                    self.warranty_gain_rate = self.supplier.issuer.warranty_gain_rate
                
                if (self.share_rate == None):
                    self.share_rate = self.supplier.issuer.share_rate

                if (self.downpayment == None):
                    self.downpayment = int(round(self.net_amount * self.supplier.downpayment_rate , -4))

                if self.additional_costs == None:
                    self.additional_costs = self.supplier.additional_costs
                try:
                    past_cont = contract.objects.get(id = self.pk)
                    if self.sign_date != past_cont.sign_date:
                        self.contract_id = None
                except:
                    pass
                if self.contract_id == None:
                    #create contract_id
                    try:
                        i = self.No()
                        if i<10:
                            i = '0' + str(i)
                        else:
                            i = str(i)
                        (year,month,day) = jalali.Gregorian(self.start_date_ins).persian_tuple()
                        self.pay_day = day
                        (year,month,day) = jalali.Gregorian(self.sign_date).persian_tuple()
                        year = year %100
                        if year < 10:
                            year = '0' + str(year)
                        if month < 10:
                            month = '0'+str(month)
                        if day < 10:
                            day = '0'+str(day)
                        date_format = (str(year),str(month),str(day))
                        date_str = "{}{}{}".format(*date_format)
                        self.contract_id = date_str + '-' + i + '-' + convert_to_englishnum(self.supplier.contract_code) + '-' + convert_to_englishnum(self.supplier.coffer.contract_code)
                    except Exception as e:
                        print(e)
                if self.status == '5' and self.original_status!=self.status:
                    localid = str(self.pk) + '8'
                    text = select_MessageText().balance_contract
                    send_sms(self.customer.mobile_number,text,localid)
                if self.vcc != None:
                        self.vcc_number = self.vcc.number
                if self.status in ['1','2','3','4']:
                    # add card for accepted contract

                    if self.vcc == None:
                        free_vcc = free_card(self.supplier.coffer)
                        if (free_vcc != None):
                            free_vcc.contract = self
                            self.vcc_number = free_vcc.number
                            self.vcc = free_vcc                
                
                if self.status == '5':
                    # free card for ended contract
                    if self.vcc != None:
                        Vcc = self.vcc
                        self.vcc = None
                        Vcc.status = '1'
                        Vcc.save()
                if self.status == '7':
                    # free card for enseraf contract
                    if self.vcc != None:
                        Vcc = self.vcc
                        self.vcc = None
                        Vcc.status = '0'
                        Vcc.save()
                if self.status in ['3','4','5','6','7']:
                    if self.clearing_date == None:
                        self.clearing_date = timezone.now().date()
        super(contract,self).save(*args,**kwargs)
        
        mine_vcc = self.vcc
        if mine_vcc != None:
            mine_vcc.status = '2'
            mine_vcc.instalment_amount = self.instalment_amount
            mine_vcc.save()
            try:
                if len(self.suretys.all()) == 0:
                    for s in Guarantee.objects.filter(customer=self.customer):
                        ContractSuretys.objects.create(cont = self, surt = s.surety, order=s.surety_order)
            except:
                pass
    
    def delete(self,*args,**kwargs):
        try:
            Vcc = self.vcc
            Vcc.status = '0'
            Vcc.save()
        except:
            pass
        return super(contract,self).delete(*args,**kwargs)

    def __str__(self):
        try:
            if self.contract_id == None:
                return str(self.id)
            else:
                return self.contract_id
        except Exception as e:
            return str(e)

SURETY_ORDER_CHOICES = (
        ('1' , 'ضامن اول') , 
        ('2' , 'ضامن دوم') ,
    )
class ContractSuretys(models.Model):
    cont = models.ForeignKey(contract ,null=False, on_delete = models.CASCADE , verbose_name = 'قرارداد' , related_name='suretys')
    order = models.CharField(max_length = 1,default='1', choices=SURETY_ORDER_CHOICES,verbose_name = 'ترتیب ضامن')
    surt = models.ForeignKey('customer.customer' ,null=False ,on_delete = models.CASCADE , verbose_name = 'ضامن', related_name='contracts')
 
    class Meta:
        verbose_name = 'ضمانت'
        verbose_name_plural = 'ضمانت'
        # ordering = [('order')]
    def __str__(self):
        return ''

class Payment(models.Model):
    amount = models.IntegerField(verbose_name = 'مبلغ' , help_text = 'ریال')
    date = models.DateField(verbose_name = 'تاریخ')
    voucher_id = models.CharField(max_length = 40 , unique = True, verbose_name = 'شماره سند بانکی')
    contract = models.ForeignKey(contract ,on_delete = models.CASCADE,related_name='payments' , verbose_name = 'قرارداد')
    VCC = models.ForeignKey( vcc ,on_delete = models.SET_NULL , 
                verbose_name = 'شماره کارت' , blank = True , null = True)
    
    class Meta:
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت ها'
        ordering = ['date']

    def save(self, *args , **kwargs):
        if self.VCC != None:
            try:
                c = self.VCC.contract
                if c.status == '6':
                    c.status = '4'
                    c.save()
                self.contract = c
            except Exception as e:
                print(str(e))
        if self.pk is None:
            flag = True
        super(payment,self).save(*args,**kwargs)
        if flag:
            if (self.VCC != None):
                Vcc = self.VCC
                Vcc.amount += self.amount
                Vcc.save()

    def add_payment(vcc_number,persian_date,amount,voucher_id):
        try:
            Vcc = vcc.objects.get(number = vcc_number)
            contract = Vcc.contract
            G_date = jalali.Persian(persian_date).gregorian_datetime()
            pay = payment(amount = amount,date = G_date , voucher_id = voucher_id)
            pay.VCC = Vcc
            pay.contract = contract
            pay.save()
            return 'موفق'
        except:
            return 0

    def jdate(self):
        return persian_numbers_converter(jalali.Gregorian(self.date).persian_string('{}/{}/{}'))
    jdate.short_description = 'تاریخ'

    def pamount(self):
        return persian_numbers_converter(self.amount, 'price')
    pamount.short_description = 'مبلغ'

    def __str__(self):
        try:
            return self.contract.customer.user.get_full_name()
        except:
            return "بدون قرارداد"

    

class Contract_coffer_info:
    def __init__(self,Contract):
        self.customer_name = Contract.customer_fullname
        self.facility = Contract.facility
        self.number_of_instalment = Contract.number_of_instalment
        self.instalment_amount = Contract.instalment_amount
        self.gain_amount = self.instalment_amount * self.number_of_instalment - self.facility
        self.instalment_start_date = Contract.jinstalment_start_date
        self.vcc_number = Contract.vcc_number
        self.supp_balance = Contract.supplier_balance
        try:
            self.balance_date = persian_numbers_converter(jalali.Gregorian(Contract.clearing_date).persian_string('{}-{}-{}'))
        except:
            self.balance_date = '0'
        self.supp_name = Contract.supplier_name
        
class Contract_info:
    def __init__(self,Contract):
        try:
            Customer = Contract.customer
            Customer_user = Contract.customer.user
            Supplier = Contract.supplier
            Supplier_user = Contract.supplier.user
            suretys =  Contract.suretys.all().order_by('order')

            if Contract.status == '7':
                self.vcc_number = ''
            else:
                self.vcc_number = Contract.vcc_number
            self.supplier_name = Supplier.name
            self.supplier_prefix = ('آقای' if Supplier.user.gender == 'm' else 'خانم')
            self.supplier_user_name = Supplier.user.get_full_name()
            self.supplier_mellicode = persian_numbers_converter(Supplier.user.melli_code)
            self.contract_id = Contract.contract_id

            self.customer_prefix = ('آقای' if Customer_user.gender == 'm' else 'خانم')
            self.customer_firstname = Customer_user.first_name
            self.customer_lastname = Customer_user.last_name
            self.customer_mobilenumber = persian_numbers_converter(Customer_user.mobile_number)
            self.customer_job = Customer.job
            self.customer_estimated = Customer.estimate_income
            try:
                year,month,day = jalali.Gregorian(Contract.sign_date).persian_tuple()
                self.sign_date_day = day
                self.sign_date_month = month
                self.sign_date_year = str(year)
                year,month,day = jalali.Gregorian(Contract.start_date_ins).persian_tuple()
                self.instalment_day = day
                self.instalment_month = month
                self.instalment_year = str(year)
                year,month,day = jalali.Gregorian(Contract.end_date).persian_tuple()
                self.end_date_day = day
                self.end_date_month = month
                self.end_date_year = str(year)
            except:
                pass

            self.net_amount = Contract.net_amount
            self.face_net_amount = Contract.face_net_amount
            self.total_amount = Contract.total_amount
            self.facility = Contract.facility
            self.loan_face_value = Contract.loan_face_value
            self.instalment_amount = Contract.instalment_amount
            self.instalment_amount_string = Contract.instalment_amount_string
            self.number_of_instalments = Contract.number_of_instalment
            self.downpayment = Contract.downpayment
            self.initial_coffer_gain = Contract.initial_coffer_gain
            self.supplier_ballance = Contract.supplier_balance
            self.discount = Contract.discount
            self.company_gain = Contract.company_gain
            self.warranty_gain_share = Contract.warranty_gain_share
            self.investor_gain = Contract.investor_gain
            self.pure_gain = Contract.pure_company_gain
            self.candi_gain = Contract.total_company_gain
            self.total_amount_of_instalments = Contract.total_amount_of_instalments
            self.total_amount_of_instalments_string = Contract.total_amount_of_instalments_string

            self.customer_fathername = Customer_user.father_name
            self.customer_mellicode = persian_numbers_converter(Customer_user.melli_code)
            self.province = Customer_user.province
            self.city = Customer_user.city
            self.address = Customer_user.address
            self.postal_code = Customer.postal_code
            self.customer_phonenumber = Customer_user.phone_number
            self.customer_workplacenumber = Customer_user.workplace_number
            self.customer_check = Contract.customer_check

            
            if len(suretys) > 0:
                surety1 =  suretys[0].surt
                self.surety1_prefix = ('آقای' if surety1.gender == 'm' else 'خانم')
                self.surety1_firstname = surety1.first_name
                self.surety1_lastname = surety1.last_name
                self.surety1_fathername = surety1.father_name
                self.surety1_mellicode  = persian_numbers_converter(surety1.melli_code)
                self.surety1_mobile_number = surety1.mobile_number
                self.surety1_job = surety1.job
                self.surety1_estimate_income = surety1.estimate_income
                self.surety1_province = surety1.province
                self.surety1_city = surety1.city
                self.surety1_address = surety1.address
                self.surety1_postalcode = persian_numbers_converter(surety1.postal_code)
                self.surety1_phonenumber = surety1.phone_number
                self.surety1_workplacenumber = surety1.workplace_number
                self.surety1_check = Contract.surety_check

            if len(suretys) > 1:
                surety2 =  suretys[1].surt
                self.surety2_prefix = ('آقای' if surety2.gender == 'm' else 'خانم')
                self.surety2_firstname = surety2.first_name
                self.surety2_lastname = surety2.last_name
                self.surety2_fathername = surety2.father_name
                self.surety2_mellicode  = persian_numbers_converter(surety2.melli_code)
                self.surety2_mobile_number = surety2.mobile_number
                self.surety2_job = surety2.job
                self.surety2_estimate_income = surety2.estimate_income
                self.surety2_province = surety2.province
                self.surety2_city = surety2.city
                self.surety2_address = surety2.address
                self.surety2_postalcode = persian_numbers_converter(surety2.postal_code)
                self.surety2_phonenumber = surety2.phone_number
                self.surety2_workplacenumber = surety2.workplace_number
                self.surety2_check = Contract.surety_check

            self.supplier_bank = Supplier.account_bank
            self.supplier_shaba = Supplier.account_shaba
            self.supplier_accountant = Supplier.accountant_name
        except ObjectDoesNotExist:
            return None

class Month_summ:
    def __init__(self,supp,start,stop):
        self.start_date = persian_numbers_converter(jalali.Gregorian(start).persian_string('{}/{}/{}'))
        self.stop_date = persian_numbers_converter(jalali.Gregorian(stop).persian_string('{}/{}/{}'))
        queryset = contract.objects.filter(sign_date__gte = start,sign_date__lte = stop,supplier = supp).exclude(status='7')
        self.supp_name = supp.name
        self.signed_num = queryset.count()
        if self.signed_num == 0:
            self.total_net_amount = 0
        else:
            self.total_net_amount = queryset.aggregate(Sum('face_net_amount'))['face_net_amount__sum']
        self.pending_num = queryset.filter(status__in=['0','1']).count()
        if self.pending_num == 0:
            self.pending_net_amount = 0
        else:
            self.pending_net_amount = queryset.filter(status__in=['0','1']).aggregate(Sum('face_net_amount'))['face_net_amount__sum']
        self.other_num = queryset.exclude(status__in=['0','1']).count()
        if self.other_num == 0:
            self.other_net_amount = 0
        else:
            self.other_net_amount = queryset.exclude(status__in=['0','1']).aggregate(Sum('face_net_amount'))['face_net_amount__sum']
        level_1 = queryset.filter(customer__level = '1')
        self.signed_num_1 = level_1.count()
        if self.signed_num_1 == 0:
            self.total_net_amount_1 = 0
        else:
            self.total_net_amount_1 = level_1.aggregate(Sum('face_net_amount'))['face_net_amount__sum']
        level_2 = queryset.filter(customer__level = '2')
        self.signed_num_2 = level_2.count()
        if self.signed_num_2 == 0:
            self.total_net_amount_2 = 0
        else:
            self.total_net_amount_2 = level_2.aggregate(Sum('face_net_amount'))['face_net_amount__sum']
        level_3 = queryset.filter(customer__level = '3')
        self.signed_num_3 = level_3.count()
        if self.signed_num_3 == 0:
            self.total_net_amount_3 = 0
        else: 
            self.total_net_amount_3 = level_3.aggregate(Sum('face_net_amount'))['face_net_amount__sum']
        self.total_company_gain = 0
        self.total_investor_gain = 0
        self.total_warranty_gain_share = 0 
        self.total_gain = 0
        for c in queryset:
            self.total_company_gain += c.company_gain
            self.total_investor_gain += c.investor_gain
            self.total_warranty_gain_share += c.warranty_gain_share
            self.total_gain += c.total_company_gain
        self.total_company_gain = self.total_company_gain
        self.total_investor_gain = self.total_investor_gain
        self.total_warranty_gain_share = self.total_warranty_gain_share 
        self.total_gain = self.total_gain

class Duration_contract(contract):
    duration = models.PositiveIntegerField( verbose_name =  'دوره پرداخت' , help_text = 'تعداد ماه')
    class Meta:
        verbose_name = 'قرارداد دوره'
        verbose_name_plural = 'قراردادهای دوره ای'
        permissions = [
            ("افراد حقوقی", "وصول مطالبات نکول شده و قرارداد های ارسال شده"),
        ]
    def __init__(self, *args, **kwargs):
        super(contract,self).__init__(*args, **kwargs)
        self.original_status = self.status
        self.original_sign_date = self.sign_date
        if self.start_date_ins is not None:
            self.instalment_start_date = self.start_date_ins
        else:
            self.instalment_start_date = self.instalment_start_datee()
        if self.pk != None:
            data ={}
            data['net_amount'] = self.net_amount
            data['face_net_amount'] = self.face_net_amount
            data['number_of_instalment'] = self.number_of_instalment
            data['additional_costs'] = self.additional_costs
            data['downpayment_rate'] = self.downpayment / self.net_amount
            data['discount'] = self.discount
            data['financial_source_rate'] = self.financial_source_rate
            data['company_gain_rate'] = self.company_gain_rate  
            data['investor_gain_rate'] = self.investor_gain_rate
            data['warranty_gain_rate'] = self.warranty_gain_rate
            data['share_rate'] = self.share_rate
            data['customer_check_factor'] = float(self.customer_check_factor)
            data['surety_check_factor'] = float(self.surety_check_factor)
            data['duration'] = int(self.duration)
            data['num_of_pay'] = int(self.number_of_instalment)
            data['sign_date'] = self.sign_date
            my_calc = main_calculation(data)
            x = my_calc.admin()

            self.discounted_net_amount = x['discounted_net_amount']
            self.loan_face_value = x['loan_face_value']
            self.supplier_balance = x['supplier_balance']
            self.company_gain = x['company_gain']
            self.investor_gain = x['investor_gain']
            
            if self.Type == '0':
                self.warranty_gain =  int(round( self.instalment_rate * self.warranty_gain_rate * (self.company_gain + self.investor_gain + self.supplier_balance) / (1-(self.instalment_rate * self.warranty_gain_rate )) ))
            elif(self.Type == '1'):
                self.warranty_gain = x['warranty_gain']   

            self.complete_gain = x['complete_gain']
            self.loan_amount = x['loan_amount']
            if (self.Type == '1'):
                self.instalment_amount = x['instalment_amount']
            elif (self.Type == '0'):
                temp =  self.loan_amount * self.instalment_rate / self.number_of_instalment
                rounded_temp = int(round(temp , -4))
                if rounded_temp - temp <-1000:
                    self.instalment_amount =  rounded_temp + 5000
                else:
                    self.instalment_amount = rounded_temp
            if self.status in ['2','3','4','5','6'] and self.amount_of_installment != None:
                self.instalment_amount = self.amount_of_installment
            self.total_amount_of_instalments = self.instalment_amount * self.number_of_instalment
            self.total_amount = self.total_amount_of_instalments + self.downpayment
            self.customer_check = x['customer_check']
            self.surety_check = x['surety_check']
            self.coffer_difference = x['coffer_difference']
            self.warranty_gain_share = x['warranty_gain_share']
            self.initial_coffer_gain = x['initial_coffer_gain']
            self.facility = x['facility']
            self.pure_company_gain = x['pure_company_gain']
            self.total_company_gain = x['total_company_gain']
            self.facility_rate = x['facility_rate']
            self.check_dates = x['check_dates']
            
    def check_date_str(self):
        x = ""
        for date in self.check_dates:
            x += "  |  " + date
        return x
    check_date_str.short_description = 'تاریخ چک ها'