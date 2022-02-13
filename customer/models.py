from datetime import datetime
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from extensions.utill import convert_to_englishnum,persian_numbers_converter
from extensions import jalali
from users.models import User

# Create your models here.

def validate_melli_code(value):
    if len(value) != 10:
        raise ValidationError(
            _('%(value)s is not valid melli code'),
            params={'value': value},
        )

def validate_mobile_number(value):
    if len(value) != 11:
        raise ValidationError(
            _('%(value)s is not mobile number code'),
            params={'value': value},
        )

def validate_phone_number(value):
    if len(value) != 11:
        raise ValidationError(
            _('%(value)s is not phone number code'),
            params={'value': value},
        )
CUSTOMER_STATUS = (
        ('00' , 'در انتظار تکمیل مدارک'),
        ('0' , 'درحال بررسی'),
        ('1' , 'تایید شده'),
        ('2' , 'رد شده'),
        ('3' , 'تایید مشروط'),
        ('4' , 'انصراف متقاضی'),
        ('5' , 'نقص مدارک'),
        ('6' , 'انقضای رتبه اعتباری'),
        )

CUSTOMER_LEVEL = (
    ('0' , 'مشخص نشده'),
    ('1','سطح ۱'),
    ('2','سطح ۲'),
    ('3','سطح ۳'),
)
CUSTOMER_JOB_CLASSES = (
    ('3', 'خصوصی'),
    ('1' , 'آزاد'),
    ('0', 'دولتی'),
    ('5', 'بازنشسته'),
    ('2' , 'مستمری بگیر'),
)
USER_GENDER_DICT = {
    'm' : 'آقای',
    'f' : 'خانم'
}
LEVEL_DICT = dict(CUSTOMER_LEVEL)

MARITAL_STATUS = (
    ('0', 'مجرد'),
    ('1', 'متاهل'),
    ('2', 'سرپرست خانوار'),
)
RELATIONSHIP_WITH_CUSTOMER = (
    ('0','پدر'),
    ('1','مادر'),
    ('2','برادر'),
    ('3','خواهر'),
    ('4','همسر'),
)
TYPE_DOCUMENT = (
    ('0', 'تک برگ'),
    ('1', 'منگوله دار'),
)
TYPE_OWNER = (
    ('0', 'مالک نیستم'),
    ('1', 'مالک هستم'),
)
HAS_CHECK = (
    ('0','خودم چک ندارم'),
    ('1', 'خودم چک دارم')
)
TYPE_MINE = (
    ('0', 'قرارداد اجاره بنام خودم است'),
    ('1', 'قرارداد اجاره بنام خودم نیست'),
)

HOME_TYPE = (
    ('0','شخصی'),
    ('2','استیجاری'),
    ('1','سازمانی'),
)
SURETY_PERMISSION_STATUS = (
    (False,'نمیتواند ضامن باشد'),
    (True,'میتواند ضامن باشد'),
)
AGAIN_PURCHASE_STATUS = (
    (False, 'نمیتواند خرید مجدد بکند'),
    (True, 'میتواند خرید مجدد بکند'),
)
CUSTOMER_JOB_STATUS = (
    ('0','قرارداد موقت (با مدت معین)'),
    ('1','قرارداد غیرموقت (دائم)'),
    ('2','بدون قرارداد'),
    ('3','با پروانه کسب یا اجاره نامه تجاری به نام'),
    ('4','بدون پروانه کسب یا اجاره نامه تجاری به نام'),
    ('5','کارکنان رسمی دولت'),
    ('6','استخدام پیمانی'),
    ('7','کارکنان خدماتی'),
    ('8','سازمان تامین اجتماعی'),
    ('9','سازمان بازنشستگی کشوری'),
    ('10','سازمان بازنشستگی نیروهای مسلح'),
    ('11','رسمی'),
    ('12','سایر'),
)
ACCEPT_REASON = (
    ('0','با مدارک اصلی'),
    ('1','همراه با مدارک تکمیلی')
)
FAULT_REASON = (
    ('0','مخدوش بودن مدارک اولیه ضروری'),
)
EXPIRE_REASON = (
    ('0','گذشت بیش از یکماه از آپلود مدارک'),
    ('1','استفاده از سقف تسهیلات یا دارای تسهیلات فعال  '),
)
CANCEL_REASON = (
    ('0','توسط فروشگاه'),
    ('1','اعلام متقاضی به ادمین '),
)
REJECT_REASON = (
    ('0','نداشتن حداقل امتیاز اعتباری کافی'),
    ('1','عدم رعایت محدودیت سنی'),
    ('2','عدم مطابقت درآمد و اقساط ماهیانه'),
    ('3','دارای سابقه نامناسب رفتاری در اقساط '),
)
class AcceptDescriptionManger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(Type='1')
class AcceptDescription(Description):
    objects = AcceptDescriptionManger()
    def save(self, *args, **kwargs):
        self.Type = '1'
        super().save(*args, **kwargs)
    class Meta:
        proxy = True
        verbose_name = 'توضیح تایید'
        verbose_name_plural = 'توضیحات تایید'
class FaultDescriptionManger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(Type='5')
class FaultDescription(Description):
    objects = FaultDescriptionManger()
    def save(self, *args, **kwargs):
        self.Type = '5'
        super().save(*args, **kwargs)
    class Meta:
        proxy = True
        verbose_name = 'توضیح نقص مدرک'
        verbose_name_plural = 'توضیحات نقص مدرک'
class ExpireDescriptionManger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(Type='6')
class ExpireDescription(Description):
    objects = ExpireDescriptionManger()
    def save(self, *args, **kwargs):
        self.Type = '6'
        super().save(*args, **kwargs)
    class Meta:
        proxy = True
        verbose_name = 'توضیح انقضای اعتبار'
        verbose_name_plural = 'توضیحات انقضای اعتبار'
class CancelDescriptionManger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(Type='4')
class CancelDescription(Description):
    objects = CancelDescriptionManger()
    def save(self, *args, **kwargs):
        self.Type = '4'
        super().save(*args, **kwargs)
    class Meta:
        proxy = True
        verbose_name = 'توضیح انصراف'
        verbose_name_plural = 'توضیحات انصراف'
class RejectDescriptionManger(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(Type='2')
class RejectDescription(Description):
    objects = RejectDescriptionManger()
    def save(self, *args, **kwargs):
        self.Type = '2'
        super().save(*args, **kwargs)
    class Meta:
        proxy = True
        verbose_name = 'توضیح رد'
        verbose_name_plural = 'توضیحات رد'
class Customer(User):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE , verbose_name = 'کاربر', parent_link=True)
      
    job = models.CharField(max_length = 30 , blank = True , verbose_name = 'عنوان شغلی')
    job_workplace = models.CharField(max_length=50, blank= True, verbose_name='محل شغل')
    job_phone_number = models.CharField(max_length=11, blank= True, verbose_name= 'شماره تماس محل کار')
    job_class = models.CharField(max_length = 1 , default = '3' ,choices = CUSTOMER_JOB_CLASSES, verbose_name = 'حوزه شغلی')
    job_status = models.CharField(max_length = 2, default = '0', choices = CUSTOMER_JOB_STATUS, verbose_name = 'وضعیت شغلی')
    job_address = models.CharField(max_length = 500, blank = True , verbose_name = 'نشانی محل کار')
    estimate_income = models.IntegerField(default = 0 , verbose_name = 'حدود درآمد ماهانه' , help_text='میلیون ریال')
    surteys = models.ManyToManyField('customer.customer', through='Guarantee')
    surety_date = models.DateField(verbose_name='تاریخ صدور ضمانت',null=True, blank=True)
    home_type = models.CharField(max_length=1, default='2', choices=HOME_TYPE, verbose_name='وضعیت ملکی')
    status = models.CharField(max_length = 2, default = '0'  ,choices = CUSTOMER_STATUS, verbose_name = 'وضعیت اولیه متقاضی')
    level = models.CharField(max_length = 1 ,default = '0', choices = CUSTOMER_LEVEL , verbose_name = 'سطح تسهیلات')
    marital_status = models.CharField(max_length= 1, default='1', choices= MARITAL_STATUS, verbose_name= 'وضعیت تاهل')
    postal_code = models.CharField(max_length = 10 ,blank = True, default = '' , verbose_name = 'کد پستی')
    credit_rank = models.CharField(max_length=1000,blank = True , verbose_name = 'شرح وضعیت')
    accept_reason = models.CharField(max_length=1, blank=True,null=True,choices=ACCEPT_REASON,verbose_name='دلیل تایید')
    accept_desc = models.ManyToManyField(AcceptDescription,related_name='accepts',blank=True, verbose_name='توضیحات تایید')
    faultdocument_reason = models.CharField(max_length=1,blank=True,null=True,choices=FAULT_REASON,verbose_name='دلیل نقص مدرک')
    faultdocument_desc = models.ManyToManyField(FaultDescription,related_name='faults',blank=True,verbose_name='توضیحات نقص مدرک')
    expire_reason = models.CharField(max_length=1,blank=True,null=True,choices=EXPIRE_REASON,verbose_name='دلیل انقضا')
    expire_desc = models.ManyToManyField(ExpireDescription,related_name='expires',blank=True,verbose_name='توضیحات انقضا')
    cancel_reason = models.CharField(max_length=1,blank=True,null=True,choices=CANCEL_REASON,verbose_name='دلیل انصراف')
    cancel_desc = models.ManyToManyField(CancelDescription,related_name='cancels',blank=True,verbose_name='توضیحات انصراف')
    reject_reason = models.CharField(max_length=1,blank=True,null=True,choices=REJECT_REASON,verbose_name='دلیل رد')
    reject_desc = models.ManyToManyField(RejectDescription,related_name='rejects',blank=True,verbose_name='توضیحات رد')
    cust_description = models.TextField(blank=True , verbose_name=' توضیحات متقاضی')
    organ_code = models.CharField(max_length = 1,blank = True, default = ''  , verbose_name = 'کد سازمان')
    organ = models.ForeignKey(Organ ,null = True,blank = True, on_delete = models.CASCADE , verbose_name = 'سازمان معرف')
    surety_permission = models.BooleanField(default=True, choices=SURETY_PERMISSION_STATUS, verbose_name='توانایی ضامن شدن' )
    again_purchase = models.BooleanField(default=True, choices=AGAIN_PURCHASE_STATUS, verbose_name='توانایی خرید مجدد')
    confirmation_date = models.DateField(verbose_name='تاریخ بررسی', null=True, blank=True)
    fileـsender = models.CharField(max_length = 200 , blank = True , verbose_name = 'صادر کننده فایل')
    credit_rating_score  = models.CharField(max_length = 200 , blank = True , verbose_name = 'نمره رتبه اعتباری')
    credit_rating_description  = models.CharField(max_length = 200 , blank = True , verbose_name = 'توصیف رتبه اعتباری')
    credit_date = models.DateField( null = True ,blank = True , verbose_name = 'تاریخ صدور گزارش رتبه اعتباری')
    
    class Meta:
        verbose_name = 'متقاضی'
        verbose_name_plural = 'متقاضیان'
        
    @property
    def marital_status_str(self):
        return dict(MARITAL_STATUS)[self.marital_status]
    @property
    def home_type_str(self):
        return dict(HOME_TYPE)[self.home_type]
    @property
    def home_owner(self):
        if self.home_type == '0': #PersonalHome
            return self.personalhome.owner_name
            return self.homestatus.owner_name
            
    def signupNo(self):
        return self.user.signupNo()
    
    def full_name(self):
        return USER_GENDER_DICT[self.user.gender] + ' ' + self.user.get_full_name()
    def instalment(self):
        sum_of_instalments = 0
        for contract in self.contract_set.filter(status__in =['2','3','4']):
            sum_of_instalments += int(contract.instalment_amount)
        return sum_of_instalments
    instalment.short_description = 'قسط'

    def save(self, *args , **kwargs):
        if self.status == '1' or self.status == '3':
            tdate =datetime.now()
            self.confirmation_date = tdate
            
        if (self.home_type == '0'): #PersonalHome
            try:
                OrganizationHome.objects.get(customer = self).delete()
            except:
                pass
            try:
                RentalHome.objects.get(customer = self).delete()
            except:
                pass
            
        elif (self.home_type == '1'): #OrganizationHome
            try:
                PersonalHome.objects.get(customer = self).delete()
            except:
                pass
            try:
                RentalHome.objects.get(customer = self).delete()
            except:
                pass
        elif (self.home_type == '2'): #RentalHome
            try:
                PersonalHome.objects.get(customer = self).delete()
            except:
                pass
            try:
                OrganizationHome.objects.get(customer = self).delete()
            except:
                pass
        super(customer,self).save(*args,**kwargs)

    def __str__(self):
        return str(self.user.get_full_name())
USER_GENDER = (
    ('m' , 'آقای'),
    ('f' , 'خانم'),
)

SURETY_ORDER = (
    ('2', 'ضامن سوم'),
    ('1', 'ضامن اول'),
    ('0', 'ضامن دوم'),
)
class Guarantee(models.Model):
    customer = models.ForeignKey('customer', on_delete = models.CASCADE, related_name= 'my_suretys', verbose_name='متقاضی')
    surety = models.ForeignKey('customer', on_delete = models.CASCADE, related_name= 'my_customers', verbose_name= 'ضامن' )
    surety_order = models.CharField(max_length=1, default='1', choices=SURETY_ORDER, verbose_name= 'ترتیب ضامن')
    
    class Meta:
            verbose_name = 'ضامن'
            verbose_name_plural = 'ضامنها'
            unique_together = ('customer', 'surety')
    def __str__(self):
        return 'نام متقاضی:' + self.customer.first_name + '\n' + 'نام ضامن:'+ self.surety.first_name

            
class Family(models.Model):
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    Type = models.CharField(max_length=1, default='0',choices=RELATIONSHIP_WITH_CUSTOMER, verbose_name='نسبت با متقاضی' )
    mobile_number = models.CharField (max_length = 11,validators=[validate_mobile_number],blank=True, verbose_name = 'شماره همراه')
    melli_code = models.CharField (max_length = 10 , validators = [validate_melli_code], blank = True , verbose_name = 'کد ملی') 
    phone_number = models.CharField(max_length=11, default = '', blank= True, verbose_name= 'تلفن ثابت')
    phone_number_description = models.CharField(max_length= 20,blank = True, verbose_name= 'عنوان تلفن ثابت')
    customer = models.OneToOneField(customer, on_delete = models.CASCADE , verbose_name = 'متقاضی')

    class Meta:
        verbose_name = 'اقوام درجه یک'
        verbose_name_plural = 'اقوام درجه یک'
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name

class HomeStatus(models.Model):
    class Meta:
        abstract = True
    customer = models.OneToOneField(customer, on_delete = models.CASCADE , verbose_name = 'متقاضی' )

class PersonalHome(HomeStatus):
    relationship = models.CharField(max_length= 20,blank=True, verbose_name='نسبت')
    first_name = models.CharField(max_length=30, blank=True, verbose_name='نام')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='نام خانوادگی')
    mobile_number = models.CharField (max_length = 11,validators=[validate_mobile_number], blank = True , verbose_name = 'شماره همراه')
    melli_code = models.CharField (max_length = 10 , validators = [validate_melli_code], blank = True  , verbose_name = 'کد ملی') 
    document_type = models.CharField(max_length=1, default='0', choices= TYPE_DOCUMENT, verbose_name='نوع سند')
    is_owner = models.CharField(max_length=1, choices=TYPE_OWNER, default='0', verbose_name=' مالک')
    unique_number = models.CharField(max_length=20 ,blank= True, verbose_name='شماره یکتا' ) 
    real_state_number = models.CharField(max_length=15,blank=True, verbose_name='شماره دفتر املاک' )
    page_number = models.SmallIntegerField(blank=True,default=0, verbose_name='شماره صفحه')

    class Meta:
        verbose_name = 'وضعیت مسکن:ملکی'
        verbose_name_plural = 'وضعیت مسکن:ملکی'
        
    @property
    def owner_name(self):
        if self.is_owner == '1':
            return 'خودم'
        else:
            return self.first_name + ' ' + self.last_name
    def __str__(self):
        return "شماره موبایل صاحب سند: " + self.mobile_number
    def save(self, *args , **kwargs):
        if self.is_owner == '1':
            self.last_name = self.customer.last_name
            self.first_name = self.customer.first_name 
            self.relationship = 'خودم'
            self.mobile_number = self.customer.mobile_number
            self.melli_code =  self.customer.melli_code
        super(PersonalHome,self).save(*args,**kwargs)
class OrganizationHome(HomeStatus):
    title = models.CharField(max_length=60,blank =True, verbose_name='عنوان سازمانی')

    class Meta:
        verbose_name = 'وضعیت مسکن:سازمانی'
        verbose_name_plural = 'وضعیت مسکن:سازمانی'
    @property
    def owner_name(self):
        return 'سازمان'
    def __str__(self):
        return 'عنوان سازمانی: '  + self.title

class RentalHome(HomeStatus):
    relationship = models.CharField(max_length= 20,blank=True, verbose_name='نسبت')
    first_name = models.CharField(max_length=30, blank=True, verbose_name='نام')
    last_name = models.CharField(max_length=150, blank=True, verbose_name='نام خانوادگی')
    mobile_number = models.CharField (max_length = 11,validators=[validate_mobile_number],blank =True, verbose_name = 'شماره همراه')
    melli_code = models.CharField (max_length = 10 , validators = [validate_melli_code], blank = True  , verbose_name = 'کد ملی')
    is_mine = models.CharField( max_length=1 ,choices=TYPE_MINE, default='0', verbose_name='طرف قرارداد')
    rental_rate = models.IntegerField(default = 0 , verbose_name = 'میزان اجاره' , help_text='میلیون ریال')
    due_date = models.DateField(editable = True, blank = True , null = True , verbose_name = 'تاریخ سررسید قرارداد' )
    tracking_code = models.CharField(max_length= 15 , blank=True, verbose_name='کد رهگیری')

    class Meta:
        verbose_name = 'وضعیت مسکن:استیجاری'
        verbose_name_plural = 'وضعیت مسکن:استیجاری'
    @property
    def owner_name(self):
        if self.is_mine == '0':
            return 'خودم'
        else:
            return self.first_name + ' ' + self.last_name
    def __str__(self):
        return 'شماره موبایل صاحب ملک اجاره ای: ' + self.mobile_number

    def save(self, *args , **kwargs):
        if self.is_mine == '0':
            self.last_name = self.customer.last_name
            self.first_name = self.customer.first_name 
            self.relationship = 'خودم'
            self.mobile_number = self.customer.mobile_number
            self.melli_code =  self.customer.melli_code
        super(RentalHome,self).save(*args,**kwargs)
    
class Financial_Information(models.Model):
    cart_amount = models.IntegerField(verbose_name = 'مبلغ سبد خرید',default=0 , help_text = 'میلیون ریال')
    number_of_instalment = models.IntegerField( default = 12 , verbose_name = 'تعداد اقساط' )
    downpayment = models.IntegerField( blank = True , verbose_name = 'پیش پرداخت' , help_text = 'میلیون ریال')
    customer = models.OneToOneField(customer, on_delete = models.CASCADE , verbose_name = 'متقاضی', related_name='financial')

    class Meta:
        verbose_name = 'اطلاعات مالی'
        verbose_name_plural = 'اطلاعات مالی'
    def __str__(self):
        return str(self.customer.user.mobile_number)
    
class Surety(models.Model):
    first_name = models.CharField (max_length = 30 ,default = '' , blank = True, verbose_name = 'نام')
    last_name = models.CharField (max_length = 30 ,default = '' , blank = True, verbose_name = 'نام خانوادگی')
    gender = models.CharField(max_length = 1 ,default = 'm',  choices = USER_GENDER , verbose_name = 'جنسیت')
    father_name = models.CharField (max_length = 30 ,default = '' , blank = True ,verbose_name = 'نام پدر')
    melli_code = models.CharField (max_length = 10, validators = [validate_melli_code] ,default = '' , blank = True, verbose_name = 'کد ملی') 
    mobile_number = models.CharField (max_length = 11, validators = [validate_mobile_number] ,default = '' , blank = True, verbose_name = 'شماره همراه')
    phone_number = models.CharField(max_length = 11, validators = [validate_phone_number] ,default = '' , blank = True, verbose_name = 'شماره منزل')
    workplace_number = models.CharField(max_length = 11, validators = [validate_phone_number] , default = '' , blank = True, verbose_name = 'شماره ضروری')
    province = models.CharField (max_length = 30 ,default = '' , blank = True, verbose_name = 'استان')
    city = models.CharField (max_length = 30 ,default = '' , blank = True, verbose_name = 'شهر')
    address = models.TextField(default = '' , blank = True, verbose_name = 'نشانی')
    postal_code = models.CharField(max_length = 10, default = '' , blank = True, verbose_name = 'کد پستی')
    estimate_income = models.IntegerField(default = 0 , verbose_name = 'حدود درآمد ماهانه' , help_text='میلیون ریال')
    job_class = models.CharField(max_length = 1 , default = '0' ,choices = CUSTOMER_JOB_CLASSES, verbose_name = 'حوزه شغلی')
    job = models.CharField (max_length = 30 , default = '' , blank = True, verbose_name = 'شغل')
    customer =  models.ForeignKey(customer, on_delete = models.CASCADE ,related_name='suretys', verbose_name = 'مضمون عنه')
    
    class Meta:
        verbose_name = 'ضامن'
        verbose_name_plural = 'ضامن ها'

    def full_address(self):
        return '، '.join((self.province,self.city,self.address))
    full_address.short_description = 'نشانی منزل'
    def get_full_name(self):
        return "{0} {1}".format(self.first_name,self.last_name)
    
    def save(self, *args , **kwargs):
        self.melli_code = convert_to_englishnum(self.melli_code)
        self.mobile_number = convert_to_englishnum(self.mobile_number)
        self.phone_number = convert_to_englishnum(self.phone_number)
        self.workplace_number = convert_to_englishnum(self.workplace_number)
        super(surety,self).save(*args,**kwargs)

    def customer_name(self):
        return self.customer.user.get_full_name()
    customer_name.short_description = 'مضمون عنه'

    def __str__(self):
        return self.first_name + ' ' + self.last_name

JOB_CLASSES_DICT = dict(CUSTOMER_JOB_CLASSES)
class Customer_info:
    def __init__(self,customer):
        user = customer.user
        suretys = customer.suretys.all()
        self.full_name = user.get_full_name()
        try:
            self.join_date = jalali.Gregorian(user.date_joined.date()).persian_string('{}/{}/{}')
        except:
            self.join_date = 'تاریخ معتبر نیست'
        self.vcc_number = '، '.join([contract.vcc_number for contract in customer.contract_set.all() if contract.vcc_number != ''])
        self.melli_code = user.melli_code
        self.mobile_number = user.mobile_number
        self.job = customer.job
        self.estimate_income = customer.estimate_income
        self.estimate_income_str = persian_numbers_converter(customer.estimate_income,'price')
        try:
            customer.customer_document.credit_rate
            temp = 'دارد'
        except:
            temp = 'ندارد'
        self.has_credit_rank = temp
        self.credit_rank = customer.credit_rank
        self.active_conts = '، '.join([contract.contract_id for contract in customer.contract_set.filter(status__in =['5','6'])])
        self.clear_conts = '، '.join([contract.contract_id for contract in customer.contract_set.filter(status__in =['1','2','3','4'])])
        self.instalment = sum([contract.instalment_amount for contract in customer.contract_set.filter(status__in =['2','3','4'])])
        self.total_amount_of_instalments = sum([contract.total_amount_of_instalments for contract in customer.contract_set.filter(status__in =['2','3','4'])])
        self.level = LEVEL_DICT[customer.level]
        self.face_net_amount = persian_numbers_converter(sum([contract.face_net_amount for contract in customer.contract_set.all()]),'price')
        self.father_name = user.father_name
        self.phone_number = user.phone_number
        self.workplace_number = user.workplace_number
        self.address = user.full_address()
        self.postalcode = customer.postal_code
        self.job_type = JOB_CLASSES_DICT[customer.job_class]
        if customer.status == '1':
            self.accept = 'تایید'
        elif customer.status == '3':
            self.reject = 'تایید مشروط'
        elif customer.status == '2':
            self.mashroot = 'رد'
        if len(suretys) > 0:
            surety1 = list(suretys)[0]
            self.surety1_name = surety1.get_full_name()
            self.surety1_melli_code = surety1.melli_code
            self.surety1_mobile_number = surety1.mobile_number
            self.surety1_job = surety1.job
            self.surety1_estimate_income = surety1.estimate_income
            self.surety1_estimate_income_str = persian_numbers_converter(surety1.estimate_income,'price')
            self.surety1_father_name = surety1.father_name
            self.surety1_phone_number = surety1.phone_number
            self.surety1_workplace_number = surety1.workplace_number
            self.surety1_address = surety1.full_address()
            self.surety1_postalcode = surety1.postal_code
            self.surety1_job_type = JOB_CLASSES_DICT[surety1.job_class]
            try:
                surety1.surety_document.credit_rate
                temp = 'دارد'
            except:
                temp = 'ندارد'
            self.surety1_has_credit_rank = temp
        if len(suretys) > 1:
            surety2 = list(suretys)[1]
            self.surety2_name = surety2.get_full_name()
            self.surety2_melli_code = surety2.melli_code
            self.surety2_mobile_number = surety2.mobile_number
            self.surety2_job = surety2.job
            self.surety2_estimate_income = surety2.estimate_income
            self.surety2_estimate_income_str = persian_numbers_converter(surety2.estimate_income,'price')
            self.surety2_father_name = surety2.father_name
            self.surety2_phone_number = surety2.phone_number
            self.surety2_workplace_number = surety2.workplace_number
            self.surety2_address = surety2.full_address()
            self.surety2_postalcode = surety2.postal_code
            self.surety2_job_type = JOB_CLASSES_DICT[surety2.job_class]
            try:
                surety2.surety_document.credit_rate
                temp = 'دارد'
            except:
                temp = 'ندارد'
            self.surety2_has_credit_rank = temp
        self.suppliers = '، '.join([supplier.name for supplier in customer.supplier_set.all() ])


class Check_information(models.Model):
    has_check = models.CharField(max_length=1,default='0', choices=HAS_CHECK, verbose_name='داشتن چک')
    sayyad_number = models.CharField (max_length = 16 ,blank=True , verbose_name = 'شماره صیاد چک')
    city = models.CharField (max_length = 30 ,default = '' , blank = True, verbose_name = 'شهر محل صدور')
    branch_name = models.CharField(max_length=30, default='', verbose_name='نام شعبه')
    branch_code = models.CharField(max_length=10, default='', verbose_name= 'کد شعبه')
    customer = models.OneToOneField(customer, on_delete = models.CASCADE , verbose_name = 'متقاضی', related_name='checkinfo')

    class Meta:
        verbose_name = 'اطلاعات چک'
        verbose_name_plural = 'اطلاعات چک ها'

    def __str__(self):
        return self.customer.user.mobile_number