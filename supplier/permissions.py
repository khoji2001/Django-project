from rest_framework.permissions import BasePermission
from .models import supplier


class IsSupplier(BasePermission):
	message = "only supplier allow"
	
	def has_permission(self, request, view):
		user = request.user
		if user.is_superuser:
			return True
		if user is not None:
			try:
				supplier.objects.get(user=user)
				return True
			except Exception as e:
				print(e)
				return False
