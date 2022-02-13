
from django.db.models import Q
from customer.models import *
from contract.models import * 
from OTP.models import MessageText
from datetime import *
from customer.models import customer
from OTP.models import select_MessageText

def confirmation_expired_sms():
    Del_date = datetime.today() - timedelta(days=25)
    customers = customer.objects.filter(Q(status = '1') | Q(status = '3')).filter(confirmation_date__lt = Del_date)
    sms_text = select_MessageText().expire_credit
    for item in customers:
        if len(contract.objects.filter(customer = item)) == 0:
            item.status = '6'
            item.save()
            send_sms(item.user.mobile_number, sms_text)
