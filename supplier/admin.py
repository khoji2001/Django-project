from django.contrib import admin
from .models import *
from .forms import SupplierCreationForm,SupplierForm
from jalali_date.admin import ModelAdminJalaliMixin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
# Register your models here.
class supplierAdmin(ModelAdminJalaliMixin, UserAdmin):
    exclude = ('customer',)
    list_display = ('name' , 'user' ,'bazaryab', 'discount_percent', 'downpayment_percent' , 'company_percent' , 'investor_percent' , 'categories')
    list_filter = ('category',) 
    readonly_fields = ('investor_gain_rate',)
    ordering = ['-date_joined']
    add_form = SupplierCreationForm
    form = SupplierForm
    fieldsets = (
        ('اطلاعات کاربری', {
            'fields': ('melli_code', 'mobile_number', 'password') }),
        ('اطلاعات شخصی',{
            'fields': ( 'first_name' ,'last_name' ,'father_name','gender','birth_date','email','education','phone_number', 'phone_number_description', 'workplace_number'
                       , 'province', 'city', 'address' ,'description' ) 
        }),
        ('اطلاعات محل کار',{
            'fields': ( 'store_phone_number', 'store_province' ,'store_city', 'store_address',)
        }),
        ('اطلاعات تجاری', {
            'fields': ( 'coffer' , 'issuer', 'name', 'website_url', 'Type', 'fcategory', 'downpayment_rate', ('max_fac1','fac1_desc') ,('max_fac2','fac2_desc') ,('max_fac3','fac3_desc') 
                       , ('max_fac4','fac4_desc') , 'company_gain_rate_one', 'company_gain_rate_two','bazaryab', 'investor_gain_rate', 'additional_costs', 'discount', 'contract_code'
                       , 'accountant_name', 'account_bank', 'account_shaba', 'category', 'products', 'brands',)
        }),
    )
    add_fieldsets = (
       ('اطلاعات کاربری', {
            'classes': ('wide',),
            'fields': ('melli_code','mobile_number', 'password1', 'password2')}
        ),
        ('اطلاعات شخصی',{
            'fields': ( 'first_name' ,'last_name' ,'father_name','gender','birth_date','email','education','phone_number', 'phone_number_description', 'workplace_number'
                       , 'province', 'city', 'address' ,'description' ) 
        }),
        ('اطلاعات محل کار',{
            'fields': ( 'store_phone_number', 'store_province' ,'store_city', 'store_address',)
        }),
        ('اطلاعات تجاری', {
            'fields': ( 'coffer' , 'issuer', 'name', 'website_url', 'Type', 'fcategory', 'downpayment_rate', ('max_fac1','fac1_desc') ,('max_fac2','fac2_desc') ,('max_fac3','fac3_desc') 
                       , ('max_fac4','fac4_desc') , 'company_gain_rate_one', 'company_gain_rate_two','bazaryab', 'investor_gain_rate', 'additional_costs', 'discount', 'contract_code'
                       , 'accountant_name', 'account_bank', 'account_shaba', 'category', 'products', 'brands',)
        }),
    )
    search_fields = ('name',)
    autocomplete_fields = ['user']

    def categories(self, obj):
        return '، '.join([category.title for category in obj.category.all() ])
    categories.short_description = 'دسته ها'
admin.site.register(supplier , supplierAdmin)

class CategoryAdmin(admin.ModelAdmin):

    prepopulated_fields = {"slug": ("title",)}
    list_display = ('title' , 'suppliers')
    search_fields = ('title',)

    def suppliers(self, obj):
        return ' ،'.join([supplier.name for supplier in obj.supplier_set.all() ])
    suppliers.short_description = 'تأمین کنندگان'
admin.site.register(Category,CategoryAdmin)

class issuerAdmin(admin.ModelAdmin):
    list_display = ('name','wgr_percent' , 'sr_percent')
    search_fields = ('customer',)
admin.site.register(issuer , issuerAdmin)

class cofferAdmin(admin.ModelAdmin):
    list_display = ( 'name' , 'fsr_percent','fsr_percent2')
    search_fields = ('name',)
admin.site.register(coffer , cofferAdmin)
class brandAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(brand, brandAdmin)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
admin.site.register(Product,ProductAdmin)
class supplierInline(admin.TabularInline):
    model = supplier
    readonly_fields = ['coffer','suppId' , 'user']
    fields = ['suppId' ,'user','coffer' ]
    extra =0 
    line = 0
    def suppId(self,obj):
        display_text = "<right><a href='/admin/supplier/supplier/{}/change/?_to_field=id&_popup=1' target='_blank'>{}</a></right>".format(obj.pk,obj.name)
        return format_html(display_text)
    suppId.short_description = 'تامین کننده'
    # def has_add_permission(self,request,obj=None):
    #     return False
    def has_delete_permission(self, request, obj=None):
        return False
class BazaryabAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ('name' , 'gain_rate')
    inlines = [supplierInline]
    fieldsets = (
        ('اطلاعات شخصی',{
            'fields': ('name' ,'father_name','gender','birth_date','melli_code','email', 'mobile_number','education','phone_number', 'phone_number_description', 'workplace_number', 'province', 'city', 'address' ,'description' ) 
        }),
        ('اطلاعات تجاری',{
            'fields': ('gain_rate','accountant_name','account_bank','account_shaba',) 
        }),
    )
    search_fields = ('name',)
admin.site.register(Bazaryab,BazaryabAdmin)
