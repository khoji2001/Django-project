# from django import forms
# from .models import MessageText


# class OTPForm(forms.Form):
#         #called on validation of the form
#     def clean(self):
#         #run the standard clean method first
#         cleaned_data=super(MessageText, self).clean()
#         x= MessageText.objects.filter(status= True)
#         if len(x)>+1:
#             raise forms.ValidationError("Passwords do not match!")

#         #always return the cleaned data
#         return cleaned_data
#     class Meta:
#             model = MessageText
#             fields = '__all__'