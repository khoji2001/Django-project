from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from OTP.models import MobileCode


class Command(BaseCommand):
	help = 'Deletes expired token'
	
	def handle(self, *args, **options):
		now = timezone.now() - timedelta(minutes=10)
		MobileCode.objects.filter(created_date__lt=now).delete()
