
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from extensions.utill import convert_to_englishnum,persian_numbers_converter
from extensions import jalali
from .managers import UserManager

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
    ('8','علوم پزشکی')
)
class User(AbstractUser):
    username = None
    mobile_number = models.CharField (max_length = 11, unique = True , validators = [validate_mobile_number] , verbose_name = 'شماره همراه')

    gender = models.CharField(max_length = 1 ,default = 'm',  choices = USER_GENDER , verbose_name = 'جنسیت')
    father_name = models.CharField (max_length = 30 , default = '' , blank = True , verbose_name = 'نام پدر')
    melli_code = models.CharField (max_length = 10 , unique=True ,validators = [validate_melli_code], null=False , verbose_name = 'کد ملی') 
    education = models.CharField(max_length=1, default= '3', choices=EDUCATION_LEVEL, verbose_name='سطح تحصیلات')
    phone_number = models.CharField(max_length = 11, validators = [validate_phone_number] , default = '', blank = True  , verbose_name = 'شماره ثابت')
    phone_number_description = models.CharField(max_length= 30,blank= True, verbose_name= 'عنوان تلفن ثابت')
    workplace_number = models.CharField(max_length = 11, validators = [validate_phone_number] , default = '', blank = True , verbose_name = 'شماره ضروری')
    birth_date = models.DateField(editable = True, blank = True , null = True , verbose_name = 'تاریخ تولد' )
    province = models.CharField (max_length = 40 , default = '', blank = True , verbose_name = 'استان')
    city = models.CharField (max_length = 40 , default = '', blank = True , verbose_name = 'شهر')
    address = models.TextField(default = '' , blank = True , verbose_name = 'نشانی')
    description = models.TextField(blank = True , verbose_name = 'توضیحات کاربر')

    USERNAME_FIELD = 'melli_code'
    REQUIRED_FIELDS = ['mobile_number']

    objects = UserManager()
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
    @property
    def jbirth_date(self):
        if self.birth_date != None:
            return persian_numbers_converter(jalali.Gregorian(self.birth_date).persian_string('{}/{}/{}') )     
    
    def full_address(self):
        return '، '.join((self.province,self.city,self.address))
    
    def signupNo(self):
        first_of_day = self.date_joined.date()
        No = User.objects.filter(date_joined__gte = first_of_day , date_joined__lte = self.date_joined).count()
        return No
        
    def save(self, *args , **kwargs):
        self.melli_code = convert_to_englishnum(self.melli_code)
        self.mobile_number = convert_to_englishnum(self.mobile_number)
        self.phone_number = convert_to_englishnum(self.phone_number)
        self.workplace_number = convert_to_englishnum(self.workplace_number)
        super(User,self).save(*args,**kwargs)

    def __str__(self):
        return self.get_full_name()