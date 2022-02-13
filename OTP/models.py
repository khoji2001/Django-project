from django.core.exceptions import ValidationError
from django.db import models
from random import randrange
from extensions.utill import convert_to_englishnum
from django.utils.translation import gettext_lazy as _

CHOICES = (
    (True , 'ارسال '),
    (False , 'عدم ارسال ' )
)
Em_ch =  (
    ('0' , 'قرار ملاقات'),
    ('1' ,'ارسال صندوق'),
    ('2' , 'اکسل فروش ماهیانه'),
	('3' , 'تسویه قرارداد بااکسل'),
	('4' , 'متقاضی و فروشگاه'),
	('5' , 'تامین کننده جدید'),
	('6' , 'تسویه با جریمه'),
	('7' , 'اعتبار سنجی'),
	('8' , ' نکول قطعی'),
	('9' , ' ایمیل تسویه با فروشگاه'),
)
dct = dict((x, y) for x, y in Em_ch)
class Emails(models.Model):
	email_type = models.CharField(max_length=1,verbose_name='نوع ایمیل',choices=Em_ch,default='0')
	ET = models.TextField(_('متن ایمیل'),blank=True)
	ST = models.CharField(_('عنوان ایمل'),blank=True,max_length=255)
	TO = models.CharField(_('گیرندگان'),help_text='برای جداسازی از , استفاده کنید',blank=True,max_length=255)
	cc = models.CharField(_('رونوشت'),blank=True,max_length=255)
	bcc = models.CharField(_('رونوشت مخفی'),blank=True,max_length=255)
	file = models.FileField(verbose_name = 'فایل',blank=True,upload_to='tass/')
	
	class Meta:
		verbose_name = "متن ایمیل "
		verbose_name_plural = "متن ایمیل ها"
		db_table = "Emailss"

	def __str__(self):
		return dct[str(self.email_type)]
class MessageText(models.Model):
	subject = models.CharField(_('عنوان بسته'),max_length=250,default = '', blank=True)
	status = models.BooleanField(_('حالت ارسال'),default=False,choices=CHOICES)
	verify_customer = models.TextField(_('پیامک تایید اعتبار'), default="""text""")

	conditional_verify = models.TextField(_('پیامک تایید اعتبار مشروط'),default="""text
""")
	defect_document = models.TextField(_('پیامک نقص مدارک'), default="""text{0}
""")
	reject_customer = models.TextField(_('پیامک رد اعتبار'), default="""text""")

	balance_contract = models.TextField(_('پیامک تسویه قرارداد'), default="""gkldf"""
	notify_debit = models.TextField(_('پیامک معوقه اقساط') , default = """text""")

	notify_instalment = models.TextField(_('پیامک یادآوری اقساط') , default = """textt""")
	good_payer = models.TextField(_('پیامک خوش حسابی') , default = """ text"""
	contract_permission_expire = models.TextField(_('پیامک لغو قرارداد') , default = """text{0}""")
	mulct_pay = models.TextField(_('پیامک پرداخت جریمه ') , default = """text{0} {1}
""")


	class Meta:
		verbose_name = "متن پیامک ها"
		verbose_name_plural = "متن پیامک ها"

	def __str__(self):
		return self.subject
	
	
	
	
	def clean(self):
		try:
			s = MessageText.objects.get(status=True)
			if (self != s) and self.status == True:
				raise ValidationError({'status': ["فقط یک بسته توانایی ارسال دارد",]})	
		except ValidationError as v:
			raise v
		except :
			pass
	
def validate_mobile_number(value):
	if len(value) != 11:
		raise ValidationError(
			_('%(value)s is not mobile number code'),
			params={'value': value},
		)


def create_token():
	return randrange(100000, 999999)

class MobileCode(models.Model):
	mobile_number = models.CharField(max_length=11,unique=True, validators=[validate_mobile_number], verbose_name='شماره همراه')
	token = models.IntegerField(default=create_token, unique=True, verbose_name='کد عضویت', auto_created=True)
	verified = models.BooleanField(default=False, auto_created=True, verbose_name='تایید شده')
	created_date = models.DateTimeField(auto_created=True, auto_now_add=True)
	
	class Meta:
		verbose_name = "کد عضویت"
		verbose_name_plural = "کد عضویت‌ها"
	
	def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
		self.mobile_number = convert_to_englishnum(self.mobile_number)
		super(MobileCode, self).save(force_insert, force_update, using, update_fields)
	
	def __str__(self):
		return str(self.mobile_number)

class IceToken(models.Model):
	token = models.CharField(max_length=300)
	expire_date = models.DateTimeField()

def select_MessageText():
	x = MessageText.objects.get(status= True)
	return x
