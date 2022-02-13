from django.urls import path
from .views import *

app_name = "OTP"

urlpatterns = [
	path('otp/', MobileCodeView.as_view(), name='mobile_code'),
	path('reset_password',ResetPasswordView.as_view(),name = 'reset_password_with_mobile_code'),
	path('ice',getValidIceToken,name = 'get_valid_ice_token'),
]
