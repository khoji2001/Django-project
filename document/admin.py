from django.contrib import admin
from .models import customer_document,contract_document,surety_document
import csv

class CustomerDocumentInline(admin.StackedInline):
    model = customer_document
    extra = 0

class ContractDocumentInline(admin.StackedInline):
    model = contract_document
    extra = 0
    def has_view_permission(self, request, obj=None):
        return True

class CustomerDocumentAdmin(admin.ModelAdmin):
    search_fields = ['customer__user__last_name','customer__user__first_name']
    autocomplete_fields = ['customer']

class SuretyDocumentAdmin(admin.ModelAdmin):
    search_fields = ['surety__first_name','surety__last_name']
    autocomplete_fields = ['surety']

class ContractDocumentAdmin(admin.ModelAdmin):
    def customer_fullname(self,obj):
        return obj.contract.customer_fullname
    customer_fullname.short_description = 'نام متقاضی'
    list_display = ['__str__' , 'customer_fullname']
    search_fields = ['contract__contract_id','contract__customer_fullname']
    autocomplete_fields = ['contract']

admin.site.register(customer_document , CustomerDocumentAdmin)
admin.site.register(contract_document , ContractDocumentAdmin)