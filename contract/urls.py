from django.urls import path
from .views import *

app_name = 'contract'

urlpatterns = [
	path('data/', ContractView.as_view(), name='contract_data'),
    path('data/<int:pk>/', contractDetail, name='contract_detail'),
    path('data/<int:pk>/payments', contractPayments, name='contract_payments'),
    path('data/<int:pk>/instalments', contractInstalments, name='contract_instalments'),
    path('admin/data/<int:pk>/', contractAdminDetail, name='contract_detail'),
    path('receive_downpayment', receive_downpayment ,name = 'receive_downpayment'),
    path('<int:c_id>/final_c/<str:type>',final_c,name='final_contract'),
    path('supp/<int:c_id>/final_c/<str:type>',final_c_supp,name='supp_final_contract'),
    path('supp/<int:c_id>/clear_receipt/<str:type>',c_receipt,name='contract_clear_receipt'),
    path('<int:c_id>/coff_c/<str:type>',coff_c,name='baygani_contract'),
    path('supp/<int:c_id>/supp_c/<str:type>',supp_c,name='supplier_contract'),
    path('<int:c_id>/cust_c/<str:type>',cust_c,name='customer_contract'),
    path('supp/<int:c_id>/cust_c/<str:type>',cust_c_supp,name='supp_customer_contract'),
    path( 'upload_payments' , payments , name = 'upload_excels') ,
    path( 'upload_vccs' , vccs , name = 'upload_vccs_excel') ,
    path( 'upload_conts' , addcontracts , name = 'upload_contracts_excel') ,
    path( 'due_contracts' , due_contracts , name = 'due_contracts') ,
    path('receive_contract', receive_contract ,name = 'receive_contract'),
    path('all/<int:c_id>/file/' , all_doc_contr , name = "contr_doc"),
    path('admin/financing' , financing , name = 'financing'),
    path('admin/vcc' , vcc_btn , name = 'vcc_btn'),
    path('admin/supplier' , supp , name = 'supp'),
    path('admin/clearing' , Cleared , name = 'Cleared'),
    path('admin/income' , income , name = 'income'),
    
]