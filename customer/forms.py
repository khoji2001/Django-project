
from OTP.views import send_sms
from OTP.models import select_MessageText
from django.forms.widgets import Select
from django import forms
from .models import customer,AcceptDescription,FaultDescription,ExpireDescription,CancelDescription,RejectDescription,Description
from customer.models import LEVEL_DICT
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext, gettext_lazy as _


class Uploadcustexcel(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

SMS_SEND_CHOICE = [
    (True,"آری"),
    (False, "خیر"),
]


class CustomerCreationForm(UserCreationForm):
    class Meta:
        model = customer
        fields = '__all__'
    
class CustomerForm(UserChangeForm):
    sms_send = forms.BooleanField(label='ارسال پیامک',required=False, widget=Select(choices=SMS_SEND_CHOICE), initial=False)
    credit_rank = forms.CharField(label='شرح وضعیت',required=False,widget=forms.Textarea(attrs={'rows': 5, 'cols': 70}))
    cust_description = forms.CharField(label='توضیحات متقاضی', required=False, widget=forms.Textarea(attrs={'rows': 5, 'cols': 70}))
    address = forms.CharField(label='نشانی ', required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 70}))
    description = forms.CharField(label='توضیحات کاربر', required=False, widget=forms.Textarea(attrs={'rows': 5, 'cols': 70}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        messages = select_MessageText()
        status = instance.status
        sms_flag = self.cleaned_data['sms_send']
        if sms_flag == True:
            if status == '1':
                    localid = str(instance.id) + '1'
                    text = messages.verify_customer.format(LEVEL_DICT[instance.level])
                    send_sms(instance.user.mobile_number ,text , localid)
            elif status == '2':
                    localid = str(instance.id) + '2'
                    text = messages.reject_customer 
                    send_sms(instance.user.mobile_number ,text , localid)
            elif status == '3':
                    localid = str(instance.id) + '3'
                    text = messages.conditional_verify.format(LEVEL_DICT[instance.level])
                    send_sms(instance.user.mobile_number ,text , localid)
            elif status == '5':
                    localid = str(instance.id) + '5'
                    text = messages.defect_document.format(instance.credit_rank)
                    send_sms(instance.user.mobile_number ,text , localid)
            elif status == '6':
                    localid = str(instance.id) + '6'
                    text = messages.expire_credit 
                    send_sms(instance.user.mobile_number ,text , localid)
        return instance
    class Meta:
        model = customer
        fields = '__all__'
        widgets = {
            'accept_desc': forms.CheckboxSelectMultiple(),
            'faultdocument_desc': forms.CheckboxSelectMultiple(),
            'expire_desc': forms.CheckboxSelectMultiple(),
            'cancel_desc': forms.CheckboxSelectMultiple(),
            'reject_desc': forms.CheckboxSelectMultiple(),
        }