from rest_framework.permissions import BasePermission
from .models import customer


class IsCustomer(BasePermission):
	message = "only customer allow"
	
	def has_permission(self, request, view):
		user = request.user
		if user.is_superuser:
			return True
		if user is not None:
			try:
				customer.objects.get(user=user)
				return True
			except Exception as e:
				print(e)
				return False
