

from .models import supplier
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms



class SupplierCreationForm(UserCreationForm):
    class Meta:
        model = supplier
        fields = '__all__'
        
class SupplierForm(UserChangeForm):
    fac1_desc = forms.CharField(label='توضیحات سطح ۱', required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 70}))
    fac2_desc = forms.CharField(label='توضیحات سطح ۲', required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 70}))
    fac3_desc = forms.CharField(label='توضیحات سطح ۳', required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 70}))
    fac4_desc = forms.CharField(label='توضیحات سطح ۴', required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 70}))

    class Meta:
        model = supplier
        fields = '__all__'