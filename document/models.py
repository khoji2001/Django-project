

from django.db import models


# Create your models here.
def customer_directory_path(instance, imagename=None):
	if imagename == None:
		# file will be download to MEDIA_ROOT/customer_documents/customer_id
		return 'customer_documents/c{0}'.format(instance.customer_id)
	else:
		# file will be uploaded to MEDIA_ROOT/customer_documents/customer_id/image_name
		return 'customer_documents/c{0}/{1}'.format(instance.customer_id, imagename)



class customer_document(models.Model):
	mellicard_front = models.FileField(upload_to=customer_directory_path, verbose_name='روی کارت ملی', null=True , blank=True)
	mellicard_behind = models.FileField(upload_to=customer_directory_path, verbose_name='پشت کارت ملی', null=True , blank=True)
	identity_firstpage = models.FileField(upload_to=customer_directory_path, verbose_name='صفحه اول شناسنامه',
										   null=True, blank=True)
	identity_description = models.FileField(upload_to=customer_directory_path, verbose_name='توضیحات شناسنامه',
											 null=True, blank=True)
	house_evidence = models.FileField(upload_to=customer_directory_path, verbose_name='مدرک سکونت', null=True,
									   blank=True)
	recommendation = models.FileField(upload_to=customer_directory_path, verbose_name='معرفی نامه سازمان',
									 null=True, blank=True)
	sayyad_check = models.FileField(upload_to=customer_directory_path, verbose_name='چک صیاد',
										   null=True, blank=True)
	postalcode_evidence = models.FileField(upload_to=customer_directory_path, verbose_name='گواهی کد پستی', null=True,
										  blank=True)
	credit_rate = models.FileField(upload_to=customer_directory_path, verbose_name='رتبه اعتباری', null=True , blank=True)
	
	caccount_turnover = models.FileField(upload_to=customer_directory_path, verbose_name='گردش حساب جاری', null=True,
										  blank=True)
	oaccount_turnover = models.FileField(upload_to=customer_directory_path,
										  verbose_name=' گردش حساب اصلی یا فیش حقوقی مهردار', null=True, blank=True)
	
	employment_certification = models.FileField(upload_to=customer_directory_path, verbose_name='گواهی اشتغال یا جواز کسب یا لیست بیمه',
												 null=True, blank=True)
	complemental = models.FileField(upload_to=customer_directory_path, verbose_name='مدارک تکمیلی', null=True,
									   blank=True)
	customer = models.OneToOneField('customer.customer', blank=False, null=False, on_delete=models.CASCADE,
									verbose_name='متقاضی')
	
	class Meta:
		verbose_name = 'مدارک متقاضی'
		verbose_name_plural = 'مدارک متقاضیان'
	
	def __str__(self):
		try:
			return self.customer.user.get_full_name()
		except:
			return 'بدون متقاضی'


def surety_directory_path(instance, imagename):
	# file will be uploaded to MEDIA_ROOT/surety_documents/surety_id/image_name
	return 'surety_documents/s{0}/{1}'.format(instance.surety.get_full_name(), imagename)


class surety_document(models.Model):
	mellicard_front = models.FileField(upload_to=surety_directory_path, verbose_name='روی کارت ملی', null=True , blank=True)
	mellicard_behind = models.FileField(upload_to=surety_directory_path, verbose_name='پشت کارت ملی', null=True,blank=True)
	identity_firstpage = models.FileField(upload_to=surety_directory_path, verbose_name='صفحه اول شناسنامه', null=True,
										   blank=True)
	identity_description = models.FileField(upload_to=surety_directory_path, verbose_name='توضیحات شناسنامه',
											 null=True, blank=True)
	house_evidence = models.FileField(upload_to=surety_directory_path, verbose_name='مدرک سکونت', null=True,
									   blank=True)
	recommendation = models.FileField(upload_to=surety_directory_path, verbose_name='معرفی نامه سازمان',
	 null=True, blank=True)
	sayyad_check = models.FileField(upload_to=surety_directory_path, verbose_name='چک صیاد',
										   null=True, blank=True)
	postalcode_evidence = models.FileField(upload_to=surety_directory_path, verbose_name='گواهی کد پستی', null=True,
										  blank=True)
	credit_rate = models.FileField(upload_to=surety_directory_path, verbose_name='رتبه اعتباری', null=True , blank=True)
	
	caccount_turnover = models.FileField(upload_to=surety_directory_path, verbose_name='گردش حساب جاری', null=True,
										  blank=True)
	oaccount_turnover = models.FileField(upload_to=surety_directory_path,
										  verbose_name=' گردش حساب اصلی یا فیش حقوقی مهردار', null=True, blank=True)
	employment_certification = models.FileField(upload_to=surety_directory_path, verbose_name='گواهی اشتغال یا جواز کسب یا لیست بیمه',
												 null=True, blank=True)
	complemental = models.FileField(upload_to=surety_directory_path, verbose_name='مدارک تکمیلی', null=True,
									   blank=True)
	surety = models.OneToOneField('customer.surety', null=True, blank=True, on_delete=models.CASCADE,
								  verbose_name='ضامن')
	
	class Meta:
		verbose_name = 'مدارک ضامن'
		verbose_name_plural = 'مدارک ضامنین'
	
	def __str__(self):
		try:
			return self.surety.__str__()
		except:
			return 'بدون ضامن'


def contract_directory_path(instance, imagename=None):
	if imagename == None:
		return 'contract_documents/{0}'.format(instance.contract_id)
	else:
		return 'contract_documents/{0}/{1}'.format(instance.contract_id, imagename)


class contract_document(models.Model):
	pre_invoice = models.FileField(upload_to=contract_directory_path, verbose_name='پیش فاکتور', null=True,
						blank=True)
	final_invoice = models.FileField(upload_to=contract_directory_path, verbose_name='فاکتور نهایی', null=True,
						blank=True)
	customer_check = models.FileField(upload_to=contract_directory_path, verbose_name='چک متقاضی', null=True 
						, blank=True)
	surety_check1 = models.FileField(upload_to=contract_directory_path, verbose_name='چک ضامن۱', null=True,
						blank=True)
	surety_check2 = models.FileField(upload_to=contract_directory_path, verbose_name='چک ضامن۲', null=True,
						blank=True)
	downpayment_receipt = models.FileField(upload_to=contract_directory_path, verbose_name='فیش واریز پیش پرداخت',
						null=True, blank=True)
	signed_contract = models.FileField(upload_to=contract_directory_path, verbose_name='قرارداد امضا شده'
						, null=True , blank= True)
	supp_c = models.FileField(upload_to=contract_directory_path, verbose_name='خلاصه قرارداد فروشگاه',
						null=True, blank=True)
	cust_c = models.FileField(upload_to=contract_directory_path, verbose_name='خلاص قرارداد مشتری',
						null=True, blank=True)
	contract = models.OneToOneField('contract.contract', null=False, blank=False, on_delete=models.CASCADE,
						verbose_name='قرارداد')
	
	class Meta:
		verbose_name = ' مدارک قرارداد'
		verbose_name_plural = ' مدارک قراردادها'
	
	def __str__(self):
		try:
			if self.contract.contract_id == None:
				return str(self.contract.id)
			return self.contract.contract_id
		except:
			return 'بدون قرارداد'
