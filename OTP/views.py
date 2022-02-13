from .serializers import MobileCodeSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from config.settings import KAVENEGAR_API_KEY
from .models import MobileCode,IceToken
from users.models import User
from kavenegar import *
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view
from datetime import datetime,timedelta
import pytz
import requests

def send_sms(mobile_number,text,localid=None):
    try:
        api = KavenegarAPI(KAVENEGAR_API_KEY)
        params = {
            'receptor': str(mobile_number),
            'message': text,
            'sender': "10009374788634",
            'localid' : localid,
            'type': 'sms',
        }
        response = api.sms_send(params)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)
		
def send_token_sms(mobile_number, token):
	try:
		api = KavenegarAPI(KAVENEGAR_API_KEY)
		params = {
			'receptor': str(mobile_number),
			'template': 'Verify',
			'token': str(token),
			'type': 'sms',
		}
		response = api.verify_lookup(params)
	except APIException as e:
		print(e)
	except HTTPException as e:
		print(e)


class MobileCodeView(APIView):
	def get(self, request):
		mobile_number = request.GET.get("mobile_number")
		try:
			mobile_code = MobileCode.objects.get(mobile_number=mobile_number)
			return Response({}, status=status.HTTP_302_FOUND)
		except Exception as e:
			print(e)
			return Response({"error": "کدی برای این شماره موبایل موجود نیست"}, status=status.HTTP_404_NOT_FOUND)
	
	def post(self, request):
		data = dict(request.data.items())
		mobile_number = data.get("mobile_number")
		melli_code = data.pop("melli_code")
		try:
			mobile_code = list(MobileCode.objects.filter(mobile_number=mobile_number))
			if datetime.now(tz=pytz.timezone('Asia/Tehran')) <= mobile_code[-1].created_date + timedelta(minutes=2):
				return Response({"error":'از درخواست قبلی کمتر از ۲ دقیقه گذشته است'},status= status.HTTP_403_FORBIDDEN)
			mobile_codes = MobileCode.objects.filter(mobile_number=mobile_number)
			mobile_codes.delete()
		except Exception as e:
			print(e)
		serializer = MobileCodeSerializer(data=data)
		if serializer.is_valid():
			exist_user1 = User.objects.filter(mobile_number = mobile_number)
			exist_user2 = User.objects.filter(melli_code = melli_code)
			if len(exist_user2) > 0:
				return Response({"error":'کاربر با این کد ملی موجود است'},status= status.HTTP_403_FORBIDDEN)
			elif len(exist_user1) > 0:
				return Response({"error":'کاربر با این شماره موبایل موجود است لطفا با مدیر تماس بگیرید'},status= status.HTTP_403_FORBIDDEN)
			else:
				mobile_code = serializer.save()
				send_token_sms(mobile_code.mobile_number, mobile_code.token)
				return Response({"mobile_number": serializer.data.get("mobile_number")}, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	def put(self, request):
		data = dict(request.data.items())
		serializer = MobileCodeSerializer(data=data)
		if serializer.is_valid():
			mobile_number = serializer.validated_data.pop("mobile_number")
			token = serializer.validated_data.pop("token")
			try:
				mobile_code = MobileCode.objects.get(token=token, mobile_number=mobile_number)
				mobile_code.verified = True
				mobile_code.save()
				return Response({"message":"کد تایید ارسالی مورد تایید است"}, status=status.HTTP_202_ACCEPTED)
			except Exception as e:
				print(e)
				return Response({"error": "کد عضویت اشتباه است"}, status=status.HTTP_406_NOT_ACCEPTABLE)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
	def get(self, request):
		melli_code = request.GET.get("melli_code")
		try:
			exist_user = User.objects.get(melli_code=melli_code)
			output = exist_user.mobile_number[:4] + "***" + exist_user.mobile_number[7:11]
			return Response({"mobile_number": output}, status=status.HTTP_200_OK)
		except Exception as e:
			print(e)
			return Response({"error": "کاربر موجود نیست"}, status=status.HTTP_404_NOT_FOUND)
	
	def post(self, request):
		data = request.data
		try:
			melli_code = data.pop("melli_code")
			exist_user = User.objects.get(melli_code = melli_code)
			mobile_number = exist_user.mobile_number
			data['mobile_number'] = mobile_number
		except User.DoesNotExist:
			return Response({"error":'کاربر با این کد ملی موجود نیست'},status= status.HTTP_403_FORBIDDEN)
		try:
			mobile_code = list(MobileCode.objects.filter(mobile_number=mobile_number))
			if datetime.now(tz=pytz.timezone('Asia/Tehran')) <= mobile_code[-1].created_date + timedelta(minutes=2):
				return Response({"error":'از درخواست قبلی کمتر از ۲ دقیقه گذشته است'},status= status.HTTP_403_FORBIDDEN)
			mobile_codes = MobileCode.objects.filter(mobile_number=mobile_number)
			mobile_codes.delete()
		except Exception as e:
			print(e)
		serializer = MobileCodeSerializer(data=data)
		if serializer.is_valid():
			mobile_code = serializer.save()
			output = mobile_number[:4] + "***" + mobile_number[7:11]
			send_token_sms(mobile_code.mobile_number, mobile_code.token)
			return Response({"message": "پیامک ارسال شد","mobile_number": output}, status=status.HTTP_201_CREATED)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def put(self, request):
		data = request.data
		serializer = MobileCodeSerializer(data=data)
		if serializer.is_valid():
			try:
				token = serializer.validated_data.get("token")
				new_password = serializer.validated_data.get("new_password")
				melli_code = serializer.validated_data.get("melli_code")
				exist_user = User.objects.get(melli_code = melli_code)
				mobile_number = exist_user.mobile_number
				if token != None:
					try:
						mobile_code = MobileCode.objects.get(token=token, mobile_number=mobile_number)
						mobile_code.verified = True
						mobile_code.save()
						return Response({"message":"کد اعتبار سنجی صحیح است"}, status=status.HTTP_202_ACCEPTED)
					except:
						return Response({"error": "کد اعتبار سنجی اشتباه است"}, status=status.HTTP_406_NOT_ACCEPTABLE)
				elif new_password != None:
					try:
						mobile_code = MobileCode.objects.get(mobile_number=mobile_number,verified=True)
						mobile_code.delete()
						exist_user.set_password(new_password)
						exist_user.save()
						return Response({"message":"رمز عبور با موفقیت تغییر یافت"}, status=status.HTTP_202_ACCEPTED)
					except Exception as e:
						return Response({"error": "کدملی اعتبار سنجی نشده است"}, status=status.HTTP_406_NOT_ACCEPTABLE)
			except User.DoesNotExist:
				return Response({"error": 'کاربر با این کدملی موجود نیست'},status= status.HTTP_403_FORBIDDEN)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
def getValidIceToken(request):
	ice_url = "https://sandboxfirm.icescoring.com/api/v1/user/authenticate"
	login_date = {"username" : "incofund" , "password" : "inCO@4593"}
	try:
		ice_token = IceToken.objects.get(pk=1)
		if ice_token.expire_date > datetime.now(tz=pytz.timezone('Asia/Tehran')):
			valid_token = ice_token.token
		else:
			a = requests.post(ice_url , data=login_date)
			response = a.json()
			valid_token = response['Data']['token']
			expire = response['Data']['tokenExpireDate']
			ice_token.token = valid_token
			ice_token.expire_date = expire
			ice_token.save()
	except:
		a = requests.post(ice_url , data=login_date)
		response = a.json()
		valid_token = response['Data']['token']
		expire = response['Data']['tokenExpireDate']
		IceToken.objects.create(id = 1,token = valid_token,expire_date=expire)
	return Response({"token" : valid_token},status=status.HTTP_200_OK)
