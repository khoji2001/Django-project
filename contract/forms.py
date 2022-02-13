from OTP.models import select_MessageText
from supplier.models import supplier,coffer,issuer
from django.db.models.fields import CharField
from .models import *
from django.contrib import admin
from django.forms import fields
from django.forms.widgets import Select
from django import forms
from django.db import models
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget
from django.contrib.admin.widgets import AutocompleteSelect
from OTP.models import MessageText


SMS_SEND_CHOICE = [
    (True,"آری"),
    (False, "خیر"),
]

class Uploadpaymentexcel(forms.Form):
	title = forms.CharField(max_length=50)
	file = forms.FileField()
	sms_send = forms.BooleanField(label='ارسال پیامک',required=False, widget=Select(choices=SMS_SEND_CHOICE), initial=False)

class Dateform(forms.Form):
    date = JalaliDateField(label="تاریخ تسویه با فروشگاه " , widget = AdminJalaliDateWidget)

class Uploadvccexcel(forms.Form):
	title = forms.CharField(max_length=50)
	file = forms.FileField()

class Uploadcontexcel(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

class FinanceForm(forms.Form):
	start_time = JalaliDateField(label="تاریخ شروع" , widget = AdminJalaliDateWidget)
	stop_time = JalaliDateField(label="تاریخ پایان" , widget = AdminJalaliDateWidget)

class FinancingForm(forms.Form):
	coffer = forms.ModelMultipleChoiceField(label="تامین کننده مالی ",widget=forms.CheckboxSelectMultiple,required=False,queryset=coffer.objects.all())
	issuer = forms.ModelMultipleChoiceField(label="صادر کننده ضمانت ",widget=forms.CheckboxSelectMultiple,required=False,queryset=issuer.objects.all())
	btnـcoffer = forms.BooleanField(label= " همه تامین کنندگان مالی",initial=False, required=False) 
	btn_issuer = forms.BooleanField(label= "همه صادر کنندگان ضمانت‌نامه",initial=False, required=False) 
class VccForm(forms.Form):
	supp = forms.ModelMultipleChoiceField(label="تامین کنندگان",required=False,widget=forms.CheckboxSelectMultiple,queryset=supplier.objects.all())
	btn =forms.BooleanField(label="همه",initial=False, required=False) 
class DueContracts(forms.Form):
	due_date = JalaliDateField(label="روز یادآوری" , widget = AdminJalaliDateWidget)

class ContractForm(forms.ModelForm):
	sms_send = forms.BooleanField(label='ارسال پیامک',required=False, widget=Select(choices=SMS_SEND_CHOICE), initial=False)
	vcc_free = forms.ModelChoiceField(label="کارت خالی ",required=False,queryset=vcc_free.objects.all())

	def save(self, commit=True):
		instance = super().save(commit=False)
		messages = select_MessageText()
		status = instance.status
		sms_flag = self.cleaned_data['sms_send']
		if (self.cleaned_data['vcc_free'] != None):
			try:
				current_vcc =  instance.vcc
				current_vcc.status = '0'
				instance.vcc = None
				current_vcc.save()
			except Exception as e:
				print(str(e))
			instance.vcc = self.cleaned_data['vcc_free']
		if sms_flag == True:
			if status == '2': 
				localid = str(instance.pk) + '7'
				text = messages.verify_contract
				send_sms(instance.customer.mobile_number,text,localid)
			if status == '5':
				localid = str(instance.pk) + '8'
				text = messages.balance_contract
				send_sms(instance.customer.mobile_number,text,localid)
			if status == '1' and instance.supplier.Type == '1' and instance.appoint_time == None:
				localid = str(instance.pk) + '9'
				text = messages.verify_supplier_contract.format(instance.supplier_name)
				send_sms(instance.customer.mobile_number,text,localid)
		return instance
	class Meta:
		model = contract
		fields = '__all__'