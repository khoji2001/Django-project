
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from extensions.utill import convert_to_englishnum

def check_mobile_number(mobile_number):
    mobile_number = convert_to_englishnum(mobile_number)
    if mobile_number.isdigit() and len(mobile_number) == 11:
        return True
    else:
        return False


class UserManager(BaseUserManager):

    def create_user(self, mobile_number, password, **extra_fields):

        if not check_mobile_number(mobile_number):
            raise ValueError(_('شماره همراه معتبر نیست'))
        mobile_number = convert_to_englishnum(mobile_number)
        user = self.model(mobile_number= mobile_number , **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, mobile_number, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('کارمندی برای ابرکاربر ضروری است'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('ابرکاربر بودن برای ابر کاربر ضروری است.'))
        return self.create_user(mobile_number, password, **extra_fields)

