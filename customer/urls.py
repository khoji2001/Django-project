from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

app_name = "customer"

urlpatterns = [
	path('customer/', CustomerRegistrationView.as_view(), name='customer_registration'),
	path('surety/', SuretyRegistrationView.as_view(), name='surety_registration'),
	path('add_supplier' , add_supplier , name = "add_requested_supplier_for_current_customer"),
	path('<int:c_id>/file/<str:type>' , customer_file , name = "customer_file"),
	path('all/<int:c_id>/file/<str:type>' , all_doc , name = "user_doc"),
	path('help' , Help , name ='customer_help_for_contract'),
	path('add_excel', addcustomers ,name='add_excel'),
	path('calculator', calculator ,name='calculator'),
]

router = DefaultRouter()
router.register('contracts', ContractViewSet, basename='contract')
urlpatterns += router.urls