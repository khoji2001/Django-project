
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User
from django import forms


class UserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = User
        fields = '__all__'


class UserChangeForm(UserChangeForm):
    address = forms.CharField(label='نشانی ', required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 70}))
    description = forms.CharField(label='توضیحات ', required=False, widget=forms.Textarea(attrs={'rows': 5, 'cols': 70}))
    
    class Meta:
        model = User
        fields = '__all__'


