from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

app_name = 'supplier'
urlpatterns = [

	path('categories', categories, name='categories'),
	path('brands', brands, name='brands'),
	path('registration/', SupplierRegistrationView.as_view(), name="suppliers_initial_register"),
	path('suppliers/', SuppliersForCustomer.as_view(), name="suppliers_for_customers"),
	path('supplier/', SupplierView.as_view(), name="supplier"),
	#path('customers/me/', SupplierCostumersView.as_view(), name="supplier"),
	path('calculator', calculator ,name='calculator'),
	# path('caltest', calctest ,name='caltest'),
	path('specialcalc', specialCalc ,name='special_calculator'),
	# path('sp', sp ,name='special'),
]

router = DefaultRouter()
router.register('customers', CustomerViewSet, basename='customer')
router.register('contracts', ContractViewSet, basename='contract')
urlpatterns += router.urls