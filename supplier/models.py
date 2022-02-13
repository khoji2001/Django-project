from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from extensions.utill import persian_numbers_converter ,convert_to_englishnum
from django.utils.translation import gettext_lazy as _
from users.models import User

def validate_rate(value):
    if value < 0 or value > 1:
        raise ValidationError(
            _('%(value)s بین ۰-۱ نیست.'),
            params={'value': value},
        )

def validate_melli_code(value):
    value = convert_to_englishnum(value)
    if len(value) != 10 or not value.isdigit():
        raise ValidationError(
            _('%(value)s کد ملی معتبر نیست.'),
            params={'value': value},
        )

def validate_mobile_number(value):
    value = convert_to_englishnum(value)
    if len(value) != 11 or not value.isdigit():
        raise ValidationError(
            _('%(value)s شماره موبایل معتبر نیست'),
            params={'value': value},
        )

def validate_phone_number(value):
    value = convert_to_englishnum(value)
    if len(value) != 11 or not value.isdigit():
        raise ValidationError(
            _('%(value)s شماره ی ثابت معتبر نیست'),
            params={'value': value},
        )
# Create your models here.

USER_GENDER = (
    ('m' , 'آقای'),
    ('f' , 'خانم'),
)

EDUCATION_LEVEL = (
    ('0', 'بی سواد'),
    ('1', 'ابتدایی'),
    ('2', 'سیکل'),
    ('3','دیپلم'),
    ('4', 'کاردانی'),
    ('5','کارشناسی'),
    ('6','کارشناسی ارشد'),
    ('7','دکتری'),
    ('8','علوم پزشکی'),
)
class Bazaryab(models.Model):
    name = models.CharField(max_length=85, verbose_name='نام بازاریاب')
    gain_rate = models.FloatField(default=0.0,verbose_name = 'کارمزد بازاریاب', validators = [validate_rate])
    mobile_number = models.CharField (max_length = 11, unique = True  , verbose_name = 'شماره همراه')

    gender = models.CharField(max_length = 1 ,default = 'm',  choices = USER_GENDER , verbose_name = 'جنسیت')
    father_name = models.CharField (max_length = 30 , default = '' , blank = True , verbose_name = 'نام پدر')
    melli_code = models.CharField (max_length = 10 , unique=True , null=False , verbose_name = 'کد ملی') 
    education = models.CharField(max_length=1, default= '3', choices=EDUCATION_LEVEL, verbose_name='سطح تحصیلات')
    phone_number = models.CharField(max_length = 11, default = '', blank = True  , verbose_name = 'شماره ثابت')
    phone_number_description = models.CharField(max_length= 30,blank= True, verbose_name= 'عنوان تلفن ثابت')
    workplace_number = models.CharField(max_length = 11 , default = '', blank = True , verbose_name = 'شماره ضروری')
    birth_date = models.DateField(editable = True, blank = True , null = True , verbose_name = 'تاریخ تولد' )
    province = models.CharField (max_length = 40 , default = '', blank = True , verbose_name = 'استان')
    city = models.CharField (max_length = 40 , default = '', blank = True , verbose_name = 'شهر')
    address = models.TextField(default = '' , blank = True , verbose_name = 'نشانی')
    description = models.TextField(blank = True , verbose_name = 'توضیحات')
    email = models.EmailField(_('ایمیل'), null=True,  blank=True)
    accountant_name = models.CharField(max_length = 80 ,blank = True , default = '', verbose_name = 'نام صاحب حساب')
    account_bank = models.CharField(max_length = 40 , blank = True ,default = '', verbose_name = 'بانک')
    account_shaba = models.CharField(max_length = 40 , blank = True ,default = '', verbose_name = 'شماره شبا')
    def __str__(self):
        return self.name

    def save(self, *args , **kwargs):
        if self.pk != None:
            b = supplier.objects.filter(bazaryab__pk = self.pk)
            for item in b:
                
                item.investor_gain_rate = self.gain_rate    
                item.save()
        return super(Bazaryab,self).save(*args,**kwargs)
    class Meta:
        verbose_name = 'بازاریاب'
        verbose_name_plural = 'بازاریاب ها'


class coffer(models.Model):
    name = models.CharField(max_length = 30 , verbose_name = 'نام تامین مالی')
    financial_source_rate1 = models.FloatField( default = 0.3 , blank =True , verbose_name = 'نرخ تسهیلات یک ساله', validators = [validate_rate])
    financial_source_rate2 = models.FloatField( default = 0.3 , blank =True , verbose_name = 'نرخ تسهیلات دو ساله', validators = [validate_rate])
    nokol_rate = models.FloatField( default = 0.02 , blank =True , verbose_name = 'نرخ کارمزد ذخیره نکول', validators = [validate_rate])
    finance_gain_rate = models.FloatField( default = 0.035 , blank =True , verbose_name = 'نرخ کارمزد تامین مالی', validators = [validate_rate])
    contract_code = models.CharField(max_length = 4, unique = True , verbose_name = 'کد قراردادی')
    contract_file = models.FileField(verbose_name='فایل خام قرارداد',null=True)
    coff_contract_file = models.FileField(verbose_name='فایل خام خلاصه صندوق',null=True,blank=True)
    cust_contract_file = models.FileField(verbose_name='فایل خام حلاصه مشتری',null=True,blank=True)
    supp_contract_file = models.FileField(verbose_name='فایل خام خلاصه تامین کننده',null=True,blank=True)
    c_receipt_file = models.FileField(verbose_name='فایل خام رسید تسویه',null=True,blank=True)

    class Meta:
        verbose_name = 'تامین کننده مالی'
        verbose_name_plural = 'تامین کننده‌های مالی'


    def save(self, *args , **kwargs):
        self.contract_code = convert_to_englishnum(self.contract_code)
        super(coffer,self).save(*args,**kwargs)

    def fsr_percent(self):
        return persian_numbers_converter(int(round(self.financial_source_rate1 * 100))) + ' درصد '
    fsr_percent.short_description = 'تسهبلات خالص یک ساله'
    def fsr_percent2(self):
        return persian_numbers_converter(int(round(self.financial_source_rate2 * 100))) + ' درصد '
    fsr_percent2.short_description = 'تسهبلات خالص دو ساله'

    def __str__(self):
        return self.name
ISSUER_TYPES = (
    ('0' , 'درابتدا'),
    ('1' ,'تدریجی'),
)
class issuer(models.Model):
    name = models.CharField(max_length = 30 , verbose_name = 'نام')
    Type = models.CharField(max_length = 1,choices = ISSUER_TYPES , verbose_name = 'نحوه محاسبه کارمزد')
    warranty_gain_rate = models.FloatField( default = 0 , blank =True , verbose_name = 'کارمزد صدور ضمانت نامه', validators = [validate_rate])
    share_rate = models.FloatField( default = 0.5 , blank =True , verbose_name = ' سهم توسعه', validators = [validate_rate])


    class Meta:
        verbose_name = 'صادرکننده ضمانت نامه'
        verbose_name_plural = 'صادرکنندگان ضمانت نامه'

    def wgr_percent(self):
        return persian_numbers_converter(int(round(self.warranty_gain_rate * 100))) + ' درصد '
    wgr_percent.short_description = 'درصد کارمزد صدور'

    def sr_percent(self):
        return persian_numbers_converter(int(round(self.share_rate * 100))) + ' درصد '
    sr_percent.short_description = 'درصد سهم توسعه'

    def __str__(self):
        return self.name


class Category(models.Model):
    title = models.CharField(max_length = 100 , verbose_name = 'عنوان')
    slug = models.SlugField(max_length = 100 , allow_unicode = True, verbose_name = 'لینک کوتاه')
    order = models.IntegerField(verbose_name = 'ترتیب نمایش')

    class Meta:
        verbose_name = 'دسته'
        verbose_name_plural = 'دسته ها'
        ordering = ['order',]

    def __str__(self):
        return self.title
def logo_directory_path(instance, imagename):
    # file will be uploaded to MEDIA_ROOT/brand/brand_slug
    return 'brand/{0}'.format(instance.slug)

class Brand(models.Model):
    title = models.CharField(max_length = 100 , verbose_name = 'عنوان')
    slug = models.SlugField(max_length = 100 , allow_unicode = True, verbose_name = 'لینک کوتاه')
    logo = models.ImageField(upload_to = logo_directory_path , verbose_name = 'تصویر' , null = True)
    order = models.IntegerField(verbose_name = 'ترتیب نمایش')

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'
        ordering = ['order',]

    def __str__(self):
        return self.title

def product_directory_path(instance, imagename):
    # file will be uploaded to MEDIA_ROOT/surety_documents/surety_id/image_name
    return 'product_image/{0}'.format( imagename)

class Product(models.Model):
    title = models.CharField(max_length = 100 , verbose_name = 'عنوان')
    slug = models.SlugField(max_length = 100 , allow_unicode = True, verbose_name = 'لینک کوتاه')
    order = models.IntegerField(verbose_name = 'ترتیب نمایش')
    image = models.ImageField(upload_to = product_directory_path , verbose_name = 'تصویر' , null =True)


    class Meta:
        verbose_name = 'محصول یا خدمت'
        verbose_name_plural = 'محصولات و خدمات'
        ordering = ['order',]

    def __str__(self):
        return self.title
SUPPLIER_TYPES = (
        ('0' , 'نوع ۱'),
        ('1' ,'نوع ۲'),
        )
SUPPLIER_FCAT = (
        ('0' , 'کالا'),
        ('1' ,'خدمات'),
        )
SUPPLIER_STATUS = (
    (True , 'نمایش داده شود'),
    (False , 'پیش نویس'),
)
class Supplier(User): 
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE ,
	verbose_name = 'نماینده', parent_link=True )
    coffer = models.ForeignKey(coffer, on_delete = models.SET_NULL, null = True ,verbose_name = 'تامین کننده مالی' )
    issuer = models.ForeignKey(issuer, on_delete = models.SET_NULL, null = True ,
	verbose_name = 'صادر کننده ضمانت نامه'  )
    name = models.CharField(max_length = 30 ,default= '', blank = False ,verbose_name = 'نشان تأمین کننده' )
    website_url = models.URLField(max_length = 200,blank = True,null =True, verbose_name = 'نشانی وبگاه')
    store_phone_number = models.CharField(max_length = 50 , verbose_name = ' شماره تماس محل کار',default= '',
	 blank = True)
    status = models.BooleanField( default = False , choices = SUPPLIER_STATUS,
	verbose_name = 'وضعیت نمایش', null = True)
    Type = models.CharField(max_length = 1 , default = '0', choices = SUPPLIER_TYPES,
	verbose_name = 'سطح دسترسی')
    fcategory = models.CharField(max_length = 1, choices = SUPPLIER_FCAT,verbose_name = 'دسته بندی کلی' 
	, default = '0')
    store_province = models.CharField (max_length = 40 , default = '', blank = True , verbose_name = 'استان محل کار')
    store_city = models.CharField (max_length = 40 , default = '', blank = True , verbose_name = ' شهر محل کار')
    store_address = models.TextField( default = '' , blank = True , verbose_name = 'نشانی محل کار')
    downpayment_rate = models.FloatField(default = 0.25 ,verbose_name = ' پیش پرداخت', validators = [validate_rate])
    company_gain_rate_one = models.FloatField(default = 0.02 , blank = True ,verbose_name = 'کارمزد شرکت یک ساله', validators = [validate_rate])
    company_gain_rate_two = models.FloatField( blank = True ,verbose_name = 'کارمزد شرکت دو ساله', validators = [validate_rate])
    investor_gain_rate = models.FloatField(default = 0 , blank = True ,verbose_name = 'کارمزد بازاریاب', validators = [validate_rate])
    additional_costs = models.IntegerField( default = 0 ,verbose_name = 'هزینه های اضافی' )
    discount = models.FloatField(verbose_name = 'تخفیف', validators = [validate_rate])
    contract_code = models.CharField(max_length = 4, unique = True , verbose_name = 'کد قراردادی')
    accountant_name = models.CharField(max_length = 80 , default = '', verbose_name = 'نام صاحب حساب')
    account_bank = models.CharField(max_length = 40 , default = '', verbose_name = 'بانک')
    account_shaba = models.CharField(max_length = 40 , default = '', verbose_name = 'شماره شبا')
    bazaryab = models.ForeignKey(Bazaryab, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='بازاریاب')
    max_fac1 = models.IntegerField(default = 120 , verbose_name = 'سقف تسهیلات (سطح ۱)' , help_text='میلیون ریال')
    fac1_desc = models.CharField(max_length = 500 , default = 'یک ضامن', verbose_name = 'توضیحات سطح ۱')
    max_fac2 = models.IntegerField(default = 150 , verbose_name = 'سقف تسهیلات (سطح ۲)' , help_text='میلیون ریال')
    fac2_desc = models.CharField(max_length = 500 , default = 'یک ضامن', verbose_name = 'توضیحات سطح ۲')
    max_fac3 = models.IntegerField(default = 300 , verbose_name = 'سقف تسهیلات (سطح ۳)' , help_text='میلیون ریال')
    fac3_desc = models.CharField(max_length = 500 , default = 'دو ضامن', verbose_name = 'توضیحات سطح ۳')
    max_fac4 = models.IntegerField(default = 300 , verbose_name = 'سقف تسهیلات (سطح ۴)' , help_text='میلیون ریال')
    fac4_desc = models.CharField(max_length = 500 , default = 'دو ضامن', verbose_name = 'توضیحات سطح ۴')

    customer = models.ManyToManyField('customer.customer' ,verbose_name = 'مشتری' ,blank = True )

    category = models.ManyToManyField(Category, verbose_name = 'دسته' ,blank = True)
    products = models.ManyToManyField(Product, verbose_name = 'محصولات' ,blank = True)
    brands = models.ManyToManyField(brand, verbose_name = 'برندها' ,blank = True)


    class Meta:
        verbose_name = 'تأمین کننده'
        verbose_name_plural = 'تأمین کنندگان'

    def fuser(self):
        return self.user.get_full_name()
    fuser.short_description = 'نماینده'


    def discount_percent(self):
        return persian_numbers_converter(int(round(self.discount * 100))) + ' درصد '
    discount_percent.short_description = 'درصد تخفیف'

    def downpayment_percent(self):
        return persian_numbers_converter(int(round(self.downpayment_rate * 100))) + ' درصد '
    downpayment_percent.short_description = 'درصد پیش پرداخت'

    def company_percent(self):
        return persian_numbers_converter(int(round(self.company_gain_rate_one * 100))) + ' درصد '
    company_percent.short_description = ' کارمزد توسعه یک ساله'

    def investor_percent(self):
        return persian_numbers_converter(int(round(self.investor_gain_rate * 100))) + ' درصد '
    investor_percent.short_description = 'کارمزد بازیاب'

    def save(self, *args , **kwargs):
        if self.company_gain_rate_two == None:
            self.company_gain_rate_two = self.company_gain_rate_one
        self.contract_code = convert_to_englishnum(self.contract_code)
        self.phone_number = convert_to_englishnum(self.phone_number)

        super(supplier,self).save(*args,**kwargs)

    def __str__(self):
        return self.name

class Abstract_supplier():

    def __init__(self , agent_firstname , agent_lastname , agent_mobile_number , brand , phone_number 
    , province , city , address , description ):
        self.agent_firstname = agent_firstname
        self.agent_lastname = agent_lastname
        self.agent_mobile_number = agent_mobile_number
        self.brand = brand 
        self.phone_number = phone_number
        self.province = province
        self.city = city
        self.address = address
        self.description = description
