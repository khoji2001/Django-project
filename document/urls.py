from django.urls import path
from .views import *

app_name = "document"

urlpatterns = [
	path('customer/', CustomerDocumentView.as_view(), name='customer_document'),
	path('surety/', SuretyDocumentView.as_view(), name='surety_document'),
	path('contract/' , ContractDocumentView.as_view() , name = 'contract_document'),
]