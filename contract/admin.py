from django.contrib import admin
from .forms import dateform
from django_postgres_extensions.models.expressions import F
from OTP.models import Emails
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter, ChoiceDropdownFilter, RelatedDropdownFilter)
from django.db import models
from django.forms import NumberInput
from django.http import FileResponse
import xlsxwriter
from datetime import date
from django.core.mail import EmailMessage
from .models import *
from customer.models import Family
from customer.models import LEVEL_DICT
from jalali_date.admin import ModelAdminJalaliMixin,StackedInlineJalaliMixin
from django.utils.html import format_html
from django.db.models import F,Count,Sum,Max,Min,ExpressionWrapper,Value,Case,When,IntegerField,DateField,FloatField
from django.db.models.functions import Cast
from document.admin import ContractDocumentInline
from extensions import jalali
from extensions.utill import persian_numbers_converter
from .forms import ContractForm
from django.contrib import messages
from django.shortcuts import render
from supplier.models import supplier
import os
from django.conf import settings

OUTPUTS_DIR = os.path.join(settings.BASE_DIR,"outputs")
HOME_TYPE = {
    '0':'شخصی',
    '2':'استیجاری',
    '1':'سازمانی',
}


class ContractInline(StackedInlineJalaliMixin,admin.StackedInline):
    model = contract
    formfield_overrides = {
        models.IntegerField : { 'widget' : NumberInput(attrs={'size' : 40})}
    }
    readonly_fields = ('customer_fullname','supplier_name','vcc_number')
    fieldsets = (
        ('اطلاعات بایگانی' , {
            'fields' : ('contract_id' ,'customer' ,'customer_fullname','supplier' ,'supplier_name'
            ,'Type' ,'vcc' ,'vcc_number' ,'description' 
            ,'clearing_date' ,'status'  ,'appoint_time')
        }),
        ('اطلاعات حسابداری' , {
            'fields' : ('net_amount' ,'number_of_instalment' ,'additional_costs' ,'downpayment' 
            ,'financial_source_rate' ,'warranty_gain_rate' ,'share_rate' ,'company_gain_rate' 
            ,'investor_gain_rate' ,'discount')
        }),
    )
    extra =0
    def has_view_permission(self,request,obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_view_permission(self, request, obj=None):
        return True
class ContractBriefInline(admin.TabularInline):
    model = contract
    readonly_fields = ['contractId','contract_detail' ,'contract_coffer' ,'contract_customer']
    fields = ['contractId','contract_detail' ,'contract_coffer' ,'contract_customer']
    extra =0 
    def contractId(self,obj):
        display_text = "<center><a href='/admin/contract/contract/{}/change' target='_blank'>{}</a></center>".format(obj.pk,obj.contract_id)
        return format_html(display_text)
    contractId.short_description = 'شماره قرارداد'
    def contract_detail(self,obj):
        display_text = "<center><a href='/contract/{}/final_c/pdf' class = 'button' target='_blank'>{}</a></center>".format(obj.pk,"شرح قرارداد")
        return format_html(display_text)
    contract_detail.short_description = ''

    def contract_coffer(self,obj):
        display_text = "<center><a href='/contract/{}/coff_c/pdf' class = 'button' target='_blank'>{}</a></center>".format(obj.pk,"فرم بایگانی")
        return format_html(display_text)
    contract_coffer.short_description = ''
    
    def contract_customer(self,obj):
        display_text = "<center><a href='/contract/{}/cust_c/pdf' class = 'button' target='_blank'>{}</a></center>".format(obj.pk,"قرارداد مشتری")
        return format_html(display_text)
    contract_customer.short_description = ''

    def has_add_permission(self,request,obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_view_permission(self, request, obj=None):
        return True
class PaymentInline(admin.TabularInline):
    model = payment
    readonly_fields = ['row','jdate','famount','debit_amount']
    fields = ['row','jdate','famount','debit_amount']
    ordering = ['date']
    extra =0 
    line = 0
    total_pay=0
    instalment_amount = 0
    def row(self,obj):
        if self.instalment_amount == 0:
            self.instalment_amount = obj.contract.instalment_amount
        self.line += 1
        display_text = "<b><a href='/admin/contract/payment/{}/change' target='_blank'>{}</a></b>".format(obj.pk,persian_numbers_converter(self.line))
        return format_html(display_text)
    row.short_description = 'ردیف'
    def jdate(self,obj):
        return persian_numbers_converter(jalali.Gregorian(obj.date).persian_string('{}/{}/{}'))
    jdate.short_description = 'تاریخ واریز'
    def famount(self,obj):
        return persian_numbers_converter(obj.amount,'price') + ' ریال'
    famount.short_description = 'مبلغ پرداخت'
    def debit_amount(self,obj):
        self.total_pay += obj.amount
        return persian_numbers_converter(self.instalment_amount * self.line - self.total_pay,'price')
    debit_amount.short_description = 'مبلغ معوق'
    def has_add_permission(self,request,obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_view_permission(self, request, obj=None):
        return True

class SuretysInline(admin.TabularInline):
    model = ContractSuretys
    extra = 0
    ordering = ['order']
    def has_view_permission(self, request, obj=None):
        return True

class ContractAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):
    change_form_template = 'admin/contract/change_form.html'
    add_form_template = 'admin/contract/change_form.html'
    fieldsets_and_inlines_order = ('f','f','i','i','i','f')
    form = ContractForm
    formfield_overrides = {
        models.IntegerField : { 'widget' : NumberInput(attrs={'size' : 40})}
    } 
    inlines = [SuretysInline,PaymentInline,ContractDocumentInline]
    readonly_fields = ('customer_fullname','customer_level','supplier_name', 'vcc_number', 'jcontract_permission_date','new_vccc','ptotal_amount_of_instalments',
                       'pcustomer_check','psurety_check','ploan_face_value','ploan_amount','psupplier_balance','pcompany_gain','pwarranty_gain','pinvestor_gain',
                       'ptotal_amount', 'ppure_gain','ptotal_company_gain',
                       'customer_melli_code','customer_birth_date','customer_marital_status','customer_address','customer_postal_code','customer_phone_number',
                       'customer_home_type','customer_home_owner','customer_father', 'customer_mobile','customer_status','customer_credit_rank','customer_description',
                       'customer_job_class','customer_job_status','customer_job','customer_estimate_income','customer_job_phone_number','customer_job_address',
                       'surety1_full_name','surety1_father','surety1_melli_code','surety1_mobile','surety1_birth_date','surety1_marital_status','surety1_address','surety1_postal_code','surety1_phone_number',
                       'surety1_home_type','surety1_home_owner','surety1_job_class','surety1_job_status','surety1_job','surety1_estimate_income','surety1_job_phone_number','surety1_job_address',
                       'surety2_full_name','surety2_father','surety2_melli_code','surety2_mobile','surety2_birth_date','surety2_marital_status','surety2_address','surety2_postal_code','surety2_phone_number',
                       'surety2_home_type','surety2_home_owner','surety2_job_class','surety2_job_status','surety2_job','surety2_estimate_income','surety2_job_phone_number','surety2_job_address')
                        
    list_display = ('__str__' ,'vcc' , 'customer', 'status' , 'customer_mobile','pnet_amount','pinstalment_amount','pnumber_of_instalment','supplier_name'
    ,'clearing_date', 'contract_file','contract_detail','contract_coffer' , 'contract_customer' ,'contract_supplier')
    list_editable = ('clearing_date', )
    list_filter = (('status',ChoiceDropdownFilter),'send_to_coffer', ('supplier__name',DropdownFilter) , ('coffer__name',DropdownFilter),'sign_date',)
    search_fields = ('contract_id','customer_fullname', 'customer__user__mobile_number')
    ordering = ['-sign_date','-contract_id']
    autocomplete_fields = ['customer','vcc']
    fieldsets = (
        ('اطلاعات عمومی اقساط' , {
            'fields' : (('customer','customer_mobile'),('vcc_free','new_vccc'),'contract_id','status','sign_date' ,'start_date_ins','amount_of_installment'
                        ,'number_of_instalment' ,'ptotal_amount_of_instalments',('customer_check_factor' ,'pcustomer_check')
                        ,('surety_check_factor','psurety_check'))
        }),
        ('اطلاعات فاکتور و تامین کننده' , {
             'fields' : ('supplier','net_amount' ,'face_net_amount','ploan_face_value' ,'downpayment','ploan_amount','psupplier_balance','clearing_date'
             ,'discount','ptotal_amount')
        }),
        ('اطلاعات حسابداری' , {
            'fields' : (('company_gain_rate','pcompany_gain'),('warranty_gain_rate' ,'share_rate','pwarranty_gain'),('investor_gain_rate','pinvestor_gain'),
             'ppure_gain','ptotal_company_gain','financial_source_rate' )
        }),
        ('متقاضی' , {
            'fields' : (('customer_fullname','customer_father','customer_melli_code','customer_birth_date','customer_marital_status','customer_address','customer_postal_code','customer_phone_number',),
                        ('customer_home_type','customer_home_owner',),('customer_job_class','customer_job_status','customer_job','customer_estimate_income','customer_job_phone_number','customer_job_address'))
        }),
        ('ضامن اول' , {
            'fields' : (('surety1_full_name','surety1_father','surety1_melli_code','surety1_mobile','surety1_birth_date','surety1_marital_status','surety1_address','surety1_postal_code','surety1_phone_number',),
                        ('surety1_home_type','surety1_home_owner',),('surety1_job_class','surety1_job_status','surety1_job','surety1_estimate_income','surety1_job_phone_number','surety1_job_address'))
        }),
        ('ضامن دوم' , {
            'fields' : (('surety2_full_name','surety2_father','surety2_melli_code','surety2_mobile','surety2_birth_date','surety2_marital_status','surety2_address','surety2_postal_code','surety2_phone_number',),
                        ('surety2_home_type','surety2_home_owner',),('surety2_job_class','surety2_job_status','surety2_job','surety2_estimate_income','surety2_job_phone_number','surety2_job_address'))
        }),
        ('اطلاعات اعتبارسنجی' , {
            'fields' : ('customer_status','customer_level','jcontract_permission_date','customer_credit_rank','customer_description')
        }),  
        ('متفرقه' , {
            'fields' : ('coffer' , 'issuer' ,'Type'  ,'invoice_date' , 'invoice_number' ,'description' ,'send_to_coffer' ,'appoint_time')
        }),
        ('پیامک' , {
            'fields' : ('sms_send',)
        }),
    )
    actions = ['export_as_excel','set_status_to_verify','send_to_coffer','update','set_date_action']
    def get_fieldsets(self, request, obj=None):
        try:
            self.cust = obj.customer
        except:
            self.cust = ''
        try:
            self.surety1 = obj.suretys.get(order='1').surt
        except:
            self.surety1 = ''
        try:
            self.surety2 = obj.suretys.get(order='2').surt
        except:
            self.surety2 = ''
        fieldset = super(contractAdmin, self).get_fieldsets(request, obj)
        if self.surety1 == '':
            fieldset = fieldset[:4] + fieldset[6:]
        elif self.surety2 == '':
            fieldset = fieldset[:5] + fieldset[6:]
        return fieldset
    
    def get_queryset(self,request):
        if 'contract.افراد حقوقی' in request.user.get_all_permissions() and not request.user.is_superuser:
            queryset = super().get_queryset(request).filter(send_to_coffer = True)   
        else:
            queryset = super().get_queryset(request)
        return queryset
    
    def get_list_filter(self, request):
        if 'contract.افراد حقوقی' in request.user.get_all_permissions() and not request.user.is_superuser:
            list_filter = () 
        else:
            list_filter = (('status',ChoiceDropdownFilter),'send_to_coffer', ('supplier__name',DropdownFilter) , ('coffer__name',DropdownFilter),'sign_date',)
        
        return list_filter
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'contract.افراد حقوقی' in request.user.get_all_permissions() and not request.user.is_superuser:
            actions = () 
        else:
            pass
        
        return actions
    def set_date_action(self, request, queryset):
        if request.POST['action'] == 'set_date_action': 
            form = dateform(request.POST)
            if request.POST.get('post') == "yes":
                if form.is_valid():
                    date = form.cleaned_data['date']
                    updated = queryset.update(clearing_date=date,status='3')
                    messages.success(request, '{0} عدد قرارداد تغییر داده شد'.format(updated))
                    suppliers = supplier.objects.all()
                    
                    for supp in suppliers:
                        x = queryset.filter(supplier = supp)
                        if len(x) > 0:
                            text = ''
                            z = 1
                            f = 0
                            
                            for con in x:
                                f += con.supplier_balance
                                text += f'\n{z} {con.customer.full_name()} { persian_numbers_converter(con.supplier_balance,"price") } ' 
                                z += 1
                            email_dict = {
                'supp_acc' : supp.account_bank,
                'acc_name' : supp.accountant_name,
                'text' : text,
                'sum' : persian_numbers_converter(f,"price"),
                'date' : persian_numbers_converter(jalali.Gregorian(date).persian_string('{}-{}-{}')),
                's_name' : supp.name
                }
                            emaill = Emails.objects.get(email_type = '9')

                            email = EmailMessage(subject = emaill.ST.format(**email_dict),body = emaill.ET.format(**email_dict) ,from_email = 'admin@test.com', to = [str(supp.email)],headers= {'Content_Type' :'text/plain'})
                            email.send()

                    try:
                        
                        create_date = jalali.Gregorian(datetime.date.today()).persian_string('{}-{}-{}')
                        workbook = xlsxwriter.Workbook(os.path.join(OUTPUTS_DIR,"فروشگاه-{}.xlsx".format(create_date)))
                        cell_format = workbook.add_format({'num_format': '#,##0'})
                        cell_format.set_align('center')
                        cell_format.set_align('vcenter')
                        cell_format.set_font_name('B Nazanin')
                        worksheet = workbook.add_worksheet()
                        worksheet.right_to_left()
                        row = 0
                        col = 0
                        worksheet.set_column(1 , 30 , 20 , cell_format)
                        worksheet.write(row, col , 'ردیف')
                        col += 1
                        for val in CONTRACT_SUPP_EXCEL.values():
                            worksheet.write(row, col , val)
                            col += 1
                        row += 1
                        col = 0
                        for c in queryset:
                            c.status = '3'
                            c.save()
                            col = 0
                            worksheet.write(row , col , row)
                            col += 1
                            cont = contract_coffer_info(c)
                            cont_dict = vars(cont)
                            for key in CONTRACT_SUPP_EXCEL:
                                data = cont_dict.get(key)
                                worksheet.write(row , col , data)
                                col += 1
                            row += 1
                        workbook.close()
                        return FileResponse(open(os.path.join(OUTPUTS_DIR,"فروشگاه-{}.xlsx".format(create_date)),'rb'),as_attachment = True)
                    except Exception as e:
                        print(str(e))
                    return
        
            else:
                form = dateform()
        else:
            form = dateform()
        

        return render(request, 'admin/contract/ddate.html',
            {
             **self.admin_site.each_context(request), 
             'title': u' انتخاب تاریخ تسویه با فروشگاه',
             'objects': queryset,
             'dateform': form,
             
             })
    set_date_action.short_description = u'تعیین کردن تاریخ تسویه با فروشگاه قرارداد های انتخاب شده'
    def customer_father(self,obj):
        return self.cust.father_name
    customer_father.short_description = 'نام پدر'
    def customer_melli_code(self,obj):
        return self.cust.melli_code
    customer_melli_code.short_description = 'کد ملی'
    def customer_birth_date(self,obj):
        return self.cust.jbirth_date
    customer_birth_date.short_description = 'تاریخ تولد'
    def customer_marital_status(self,obj):
        return self.cust.marital_status_str
    customer_marital_status.short_description = 'وضعیت تاهل'
    def customer_address(self,obj):
        return self.cust.full_address()
    customer_address.short_description = 'نشانی'
    def customer_postal_code(self,obj):
        return self.cust.postal_code
    customer_postal_code.short_description = 'کد پستی'
    def customer_phone_number(self,obj):
        return self.cust.phone_number
    customer_phone_number.short_description = 'تلفن ثابت محل سکونت'
    def customer_home_type(self,obj):
        return self.cust.home_type_str
    customer_home_type.short_description = 'وضعیت مسکن'
    def customer_home_owner(self,obj):
        return self.cust.home_owner
    customer_home_owner.short_description = 'وضعیت مالک مسکن'
    def customer_job_class(self,obj):
        return self.cust.get_job_class_display()
    customer_job_class.short_description = 'حوزه شغلی'
    def customer_job_status(self,obj):
        return self.cust.get_job_status_display()
    customer_job_status.short_description = 'وضعیت شغلی'
    def customer_job(self,obj):
        return self.cust.job
    customer_job.short_description = 'عنوان شغلی'
    def customer_estimate_income(self,obj):
        return self.cust.estimate_income
    customer_estimate_income.short_description = 'درآمد تخمینی(میلیون ریال)'
    def customer_job_phone_number(self,obj):
        return self.cust.job_phone_number
    customer_job_phone_number.short_description = 'تلفن محل کار'
    def customer_job_address(self,obj):
        return self.cust.job_address
    customer_job_address.short_description = 'نشانی محل کار'
    def customer_status(self,obj):
        return self.cust.get_status_display()
    customer_status.short_description = 'وضعیت اولیه متقاضی'
    def customer_credit_rank(self,obj):
        return self.cust.credit_rank
    customer_credit_rank.short_description = 'شرح وضعیت'
    def customer_description(self,obj):
        return self.cust.cust_description
    customer_description.short_description = 'توضیحات متقاضی'
    def surety1_full_name(self,obj):
        return self.surety1.get_full_name()
    surety1_full_name.short_description = 'نام و نام خانوادگی'
    def surety1_father(self,obj):
        return self.surety1.father_name
    surety1_father.short_description = 'نام پدر'
    def surety1_melli_code(self,obj):
        return self.surety1.melli_code
    surety1_melli_code.short_description = 'کد ملی'
    def surety1_mobile(self,obj):
        return self.surety1.mobile_number
    surety1_mobile.short_description = 'شماره همراه'
    def surety1_birth_date(self,obj):
        return self.surety1.jbirth_date
    surety1_birth_date.short_description = 'تاریخ تولد'
    def surety1_marital_status(self,obj):
        return self.surety1.marital_status_str
    surety1_marital_status.short_description = 'وضعیت تاهل'
    def surety1_address(self,obj):
        return self.surety1.full_address()
    surety1_address.short_description = 'نشانی'
    def surety1_postal_code(self,obj):
        return self.surety1.postal_code
    surety1_postal_code.short_description = 'کد پستی'
    def surety1_phone_number(self,obj):
        return self.surety1.phone_number
    surety1_phone_number.short_description = 'تلفن ثابت محل سکونت'
    def surety1_home_type(self,obj):
        return self.surety1.home_type_str
    surety1_home_type.short_description = 'وضعیت مسکن'
    def surety1_home_owner(self,obj):
        return self.surety1.home_owner
    surety1_home_owner.short_description = 'وضعیت مالک مسکن'
    def surety1_job_class(self,obj):
        return self.surety1.get_job_class_display()
    surety1_job_class.short_description = 'حوزه شغلی'
    def surety1_job_status(self,obj):
        return self.surety1.get_job_status_display()
    surety1_job_status.short_description = 'وضعیت شغلی'
    def surety1_job(self,obj):
        return self.surety1.job
    surety1_job.short_description = 'عنوان شغلی'
    def surety1_estimate_income(self,obj):
        return self.surety1.estimate_income
    surety1_estimate_income.short_description = 'درآمد تخمینی(میلیون ریال)'
    def surety1_job_phone_number(self,obj):
        return self.surety1.job_phone_number
    surety1_job_phone_number.short_description = 'تلفن محل کار'
    def surety1_job_address(self,obj):
        return self.surety1.job_address
    surety1_job_address.short_description = 'نشانی محل کار'
    def surety2_full_name(self,obj):
        return self.surety2.get_full_name()
    surety2_full_name.short_description = 'نام و نام خانوادگی'
    def surety2_father(self,obj):
        return self.surety2.father_name
    surety2_father.short_description = 'نام پدر'
    def surety2_melli_code(self,obj):
        return self.surety2.melli_code
    surety2_melli_code.short_description = 'کد ملی'
    def surety2_mobile(self,obj):
        return self.surety2.mobile_number
    surety2_mobile.short_description = 'شماره همراه'
    def surety2_birth_date(self,obj):
        return self.surety2.jbirth_date
    surety2_birth_date.short_description = 'تاریخ تولد'
    def surety2_marital_status(self,obj):
        return self.surety2.marital_status_str
    surety2_marital_status.short_description = 'وضعیت تاهل'
    def surety2_address(self,obj):
        return self.surety2.full_address()
    surety2_address.short_description = 'نشانی'
    def surety2_postal_code(self,obj):
        return self.surety2.postal_code
    surety2_postal_code.short_description = 'کد پستی'
    def surety2_phone_number(self,obj):
        return self.surety2.phone_number
    surety2_phone_number.short_description = 'تلفن ثابت محل سکونت'
    def surety2_home_type(self,obj):
        return self.surety2.home_type_str
    surety2_home_type.short_description = 'وضعیت مسکن'
    def surety2_home_owner(self,obj):
        return self.surety2.home_owner
    surety2_home_owner.short_description = 'وضعیت مالک مسکن'
    def surety2_job_class(self,obj):
        return self.surety2.get_job_class_display()
    surety2_job_class.short_description = 'حوزه شغلی'
    def surety2_job_status(self,obj):
        return self.surety2.get_job_status_display()
    surety2_job_status.short_description = 'وضعیت شغلی'
    def surety2_job(self,obj):
        return self.surety2.job
    surety2_job.short_description = 'عنوان شغلی'
    def surety2_estimate_income(self,obj):
        return self.surety2.estimate_income
    surety2_estimate_income.short_description = 'درآمد تخمینی(میلیون ریال)'
    def surety2_job_phone_number(self,obj):
        return self.surety2.job_phone_number
    surety2_job_phone_number.short_description = 'تلفن محل کار'
    def surety2_job_address(self,obj):
        return self.surety2.job_address
    surety2_job_address.short_description = 'نشانی محل کار'
    def pcustomer_check(self,obj):
        return persian_numbers_converter(obj.customer_check,'price')
    pcustomer_check.short_description = 'چک متقاضی'
    def psurety_check(self,obj):
        return persian_numbers_converter(obj.surety_check,'price')
    pcustomer_check.short_description = 'چک ضامن'
    def ppure_gain(self,obj):
        return persian_numbers_converter(obj.pure_company_gain,'price')
    ppure_gain.short_description = 'درآمد خالص طرح'
    def new_vccc(self,obj):
        if obj.vcc != None:
            display_text = "<right><a href='/admin/contract/vcc/{}/change/' target='_blank'>{}</a></right>".format(obj.vcc.pk,obj.vcc_number)
        else:
            display_text = "{}".format(obj.vcc_number)
        return format_html(display_text)
    new_vccc.short_description = ' شماره کارت'
    def contract_file(self,obj):
        display_text = "<center><a href='/contract/all/{}/file/' target='_blank'>فایل قرارداد</a></center>".format(obj.pk)
        return format_html(display_text)
    contract_file.short_description = 'فایل قرارداد'
    def customer_level(self,obj):
        return LEVEL_DICT[obj.customer.level]
    customer_level.short_description = 'سطح تسهیلات متقاضی'
    def contract_detail(self,obj):
        display_text = "<center><a href='/contract/{}/final_c/pdf' class = 'button' target='_blank'>{}</a></center>".format(obj.pk,"شرح قرارداد")
        return format_html(display_text)
    contract_detail.short_description = format_html("<pre>        </pre>")

    def contract_coffer(self,obj):
        display_text = "<center><a href='/contract/{}/coff_c/pdf' class = 'button' target='_blank'>{}</a></center>".format(obj.pk,"فرم بایگانی")
        return format_html(display_text)
    contract_coffer.short_description = format_html("<pre>        </pre>")
    
    def contract_customer(self,obj):
        display_text = "<center><a href='/contract/{}/cust_c/pdf' class = 'button' target='_blank'>{}</a></center>".format(obj.pk,"قرارداد مشتری")
        return format_html(display_text)
    contract_customer.short_description = format_html("<pre>            </pre>")

    def contract_supplier(self,obj):
        display_text = "<center><a href='/contract/supp/{}/supp_c/pdf' class = 'button' target='_blank'>{}</a></center>".format(obj.pk,"قرارداد تامین کننده")
        return format_html(display_text)
    contract_supplier.short_description = format_html("<pre>            </pre>")
    def pcustomer_check(self,obj):
        return persian_numbers_converter(obj.customer_check , 'price')
    pcustomer_check.short_description = 'چک متقاضی'

    def psurety_check(self,obj):
        return persian_numbers_converter(obj.surety_check , 'price')
    psurety_check.short_description = 'چک ضامن'
    def jcontract_permission_date(self,obj):
        if obj.contract_permission_date != None:
            return persian_numbers_converter(jalali.Gregorian(obj.contract_permission_date).persian_string('{}/{}/{}'))  
        else:
            return '-'
    jcontract_permission_date.short_description = 'تاریخ صدور مجوز قرارداد'
    def set_status_to_verify(modeladmin, request, queryset):
        for c in queryset:
            c.status = '2'
            c.save()
    set_status_to_verify.short_description = 'تایید و ارسال کالای قراردادهای انتخاب شده'

    def export_as_excel(modeladmin, request, queryset):
        init_row = ['ردیف' , 'شماره کارت' , 'فروشنده', 'شماره قرارداد','جنسیت دریافت کننده', 'نام دریافت کننده', 
        'نام خانوادگی دریافت کننده', 'شماره همراه', 'شغل خریدار', 'درآمد تخمینی خریدار(میلیون تومان)' 
        , 'تاریخ عقد قرارداد (روز)' , 'تاریخ عقد قرارداد (ماه)' , 'تاریخ عقد قرارداد (سال)'
        , 'تاریخ اولین پرداخت (روز)' , 'تاریخ اولین پرداخت (ماه)' , 'تاریخ اولین پرداخت (سال)'
        , 'بهای فروش نقدی(فاکتور)' ,'فاکتور ظاهری', 'مبلغ کل اقساط','مبلغ کل اقساط به حروف', 'تسهیلات' , 'عدد ظاهری وام' 
        , 'مبلغ هر قسط','مبلغ هر قسط به حروف' , 'تعداد اقساط' , 'پیش‌پرداخت' , 'کارمزد در ابتدای صندوق(مابه التفاوت قدیم)' 
        , 'تسویه با فروشنده' , 'درصد تخفیف' , 'کارمزد طرح از فاکتور' , 'کارمزد طرح از ضمانت نامه' 
        , 'درآمد بازاریاب','درآمد خالص طرح' , 'تسویه با طرح', 'بهای فروش اقساطی'
        , 'نام پدر' , 'شماره ملی' , 'استان محل سکونت' , 'شهر محل سکونت' , 'نشانی' 
        , 'کدپستی' , 'تلفن منزل' , 'تلفن محل کار' , 'چک خریدار'
        ,'جنسیت ضامن اول', 'نام ضامن اول' , 'نام خانوادگی ضامن اول' , 'پدر ضامن اول' , 'شماره ملی ضامن اول' 
        , 'شماره موبایل ضامن اول' , 'شغل ضامن اول' , 'درآمد تخمینی ضامن اول(میلیون تومان)' 
        , 'استان ضامن اول' , 'شهر ضامن اول' ,'آدرس محل سکونت ضامن اول' ,'کدپستی ضامن اول' 
        ,'شماره تلفن ضامن اول' ,'شماره محل کار ضامن اول' ,'چک ضامن اول' 
        ,'جنسیت ضامن دوم','نام ضامن دوم' ,'نام خانوادگی ضامن دوم' ,'پدر ضامن دوم' ,'شماره ملی ضامن دوم' 
        ,'شماره موبایل ضامن دوم' ,'شغل ضامن دوم' ,'درآمد تخمینی ضامن دوم(میلیون تومان)' ,'استان ضامن دوم' 
        ,'شهر ضامن دوم' ,'آدرس محل سکونت ضامن دوم' ,'کدپستی ضامن دوم' ,'شماره تلفن ضامن دوم' 
        , 'شماره محل کار ضامن دوم' , 'چک ضامن دوم','جنسیت تامین کننده','نام و نام خانوادگی تامین کننده'
        ,'کد ملی تامین کننده' ,'صاحب حساب فروشگاه','شماره شبا فروشگاه' , 'نام بانک صاحب حساب'
        , 'تاریخ آخرین پرداخت (روز)' , 'تاریخ آخرین پرداخت (ماه)' , 'تاریخ آخرین پرداخت (سال)']

        workbook = xlsxwriter.Workbook(os.path.join(OUTPUTS_DIR,"contracts_excel.xlsx"))
        cell_format = workbook.add_format({'num_format': '#,###'})
        cell_format.set_align('center')
        cell_format.set_align('vcenter')
        cell_format.set_font_name('B Nazanin')
        worksheet = workbook.add_worksheet()
        worksheet.right_to_left()
        row = 0
        col = 0
        worksheet.set_column(1 , 82 , 20 , cell_format)
        for data in init_row:
            worksheet.write(row, col , data)
            col += 1
        row += 1
        col = 0
        for c in queryset:
            col = 0
            worksheet.write(row , col , row)
            col += 1
            contract = contract_info(c)
            contract_dict = vars(contract)
            for key in CONTRACT_EXCEL:
                data = contract_dict.get(key)
                worksheet.write(row , col , data)
                col += 1
            row += 1
        col = 0
        worksheet.write(row,col,'مجموع')
        col += 1
        sum_formula = '=SUM({0}{1}:{0}{2})'
        for val in CONTRACT_EXCEL.values():
            if isinstance(val,str):
                worksheet.write(row,col,sum_formula.format(val,'2',str(row)))
            col += 1
        workbook.close() 
        return FileResponse(open(os.path.join(OUTPUTS_DIR,"contracts_excel.xlsx"),'rb'),as_attachment = True)
    export_as_excel.short_description = 'خروجی اکسل قراردادهای انتخاب شده'
    def send_to_coffer(modeladmin,request,queryset):
        create_date = jalali.Gregorian(date.today()).persian_string('{}-{}-{}')
        workbook = xlsxwriter.Workbook(os.path.join(OUTPUTS_DIR,"تست-{}.xlsx".format(create_date)))
        cell_format = workbook.add_format({'num_format': '#,##0'})
        cell_format.set_align('center')
        cell_format.set_align('vcenter')
        cell_format.set_font_name('B Nazanin')
        worksheet = workbook.add_worksheet()
        worksheet.right_to_left()
        row = 0
        col = 0
        worksheet.set_column(1 , 30 , 20 , cell_format)
        worksheet.write(row, col , 'ردیف')
        col += 1
        for val in CONTRACT_COFFER_EXCEL.values():
            worksheet.write(row, col , val)
            col += 1
        row += 1
        col = 0
        for c in queryset:
            col = 0
            worksheet.write(row , col , row)
            col += 1
            cont = contract_coffer_info(c)
            cont_dict = vars(cont)
            for key in CONTRACT_COFFER_EXCEL:
                data = cont_dict.get(key)
                worksheet.write(row , col , data)
                col += 1
            row += 1
            c.send_to_coffer = True
            c.save()
        workbook.close()
        email_dict = {
                'date' : create_date,
                }
        emaill  = Emails.objects.get(email_type = '1')
        too = [x.strip() for x in emaill.TO.split(',')]
        bc = [x.strip() for x in emaill.bcc.split(',')]
        email = EmailMessage(subject = emaill.ST.format(**email_dict),body = emaill.ET,from_email = 'admin@test.com', to = too ,bcc=bc ,headers= {'Content_Type' :'text/plain'})
        email.attach_file(os.path.join(OUTPUTS_DIR,"تست-{}.xlsx".format(create_date)))
        email.send()
        return FileResponse(open(os.path.join(OUTPUTS_DIR,"تست-{}.xlsx".format(create_date)),'rb'),as_attachment = True)
    send_to_coffer.short_description = 'ارسال به تامین مالی قراردادهای انتخاب شده'

    def update(modeladmin,request,queryset):
        for c in queryset:
            if c.sign_date != None:
                c.amount_of_installment = c.instalment_amount
                c.save()
                year,month,day = jalali.Gregorian(c.start_date_ins).persian_tuple()
                c.pay_day = day
                c.save()
    update.short_description = 'ثبت روز پرداخت قراردادهای انتخاب شده'
class PaymentAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):
    
    formfield_overrides = {
        models.IntegerField : { 'widget' : NumberInput(attrs={'size' : 40})}
    }
    list_display = ('__str__','pamount' , 'jdate' , 'contract' , 'VCC')
    list_filter = ('date' , ('contract__contract_id',DropdownFilter ))
    search_fields = ( 'contract__contract_id', 'VCC__number','contract__customer_fullname')
    ordering = ['-date', ]
    autocomplete_fields = ['contract','VCC']

VCC_STATUSES = {
    '0' : 'آزاد',
    '1' :'مصرف شده',
    '2' : 'در حال استفاده',
}
class Contract_statusFilter(admin.SimpleListFilter):
    template = 'django_admin_listfilter_dropdown/dropdown_filter.html'
    title = 'وضعیت قرارداد '
    parameter_name = 'contract_status'
    def lookups(self, request, model_admin):
        
            return (
               
                ('4' , 'پرداخت اقساط توسط متقاضی'),
                
                ('6' , 'نکول قطعی'),
                
            )

    def queryset(self, request, queryset):
       
        if self.value() is None:
            return queryset
        else:
            return queryset.filter(contract__status = self.value())
class StatusFilter(admin.SimpleListFilter):
    template = 'django_admin_listfilter_dropdown/dropdown_filter.html'
    title = ' وضعیت '
    parameter_name = 'vcc_status'
    def lookups(self, request, model_admin):
        
            return (
                (1, 'مصرف شده'),
                (2, 'در حال استفاده'),
            )

    def queryset(self, request, queryset):
        
        if self.value() is None:
            return queryset
        elif int(self.value()) == 1:
            return queryset.filter(status = 1)
        elif int(self.value()) == 2:
            return queryset.filter(status = 2)
class DebitFilter(admin.SimpleListFilter):
    template = 'django_admin_listfilter_dropdown/dropdown_filter.html'
    title = ' معوق '
    parameter_name = 'debit_amount'
    def lookups(self, request, model_admin):
        
            return (
                (10, '10+'),
                (9, '9'),
                (8, '8'),
                (7, '7'),
                (6, '6'),
                (5, '5'),
                (4, '4'),
                (3, '3'),
                (2, '2'),
                (1, '1'),
                (0, '0'),
            )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        elif int(self.value()) in range(11):
            if int(self.value()) == 10:
                return queryset.filter(number_of_debit__gte = int(self.value()) )
            return queryset.filter(number_of_debit__gte = int(self.value()),number_of_debit__lt = 1 + int(self.value()))
class DayFilter(admin.SimpleListFilter):
    template = 'django_admin_listfilter_dropdown/dropdown_filter.html'
    title = ' روز پرداخت '
    parameter_name = 'pay_day_amount'
    def lookups(self, request, model_admin):
            return (
                (31, '31'),
                (30, '30'),
                (29, '29'),
                (28, '28'),
                (27, '27'),
                (26, '26'),
                (25, '25'),
                (24, '24'),
                (23, '23'),
                (22, '22'),
                (21, '21'),
                (20, '20'),
                (20, '20'),
                (19, '19'),
                (18, '18'),
                (17, '17'),
                (16, '16'),
                (15, '15'),
                (14, '14'),
                (13, '13'),
                (12, '12'),
                (11, '11'),
                (10, '10'),
                (9, '9'),
                (8, '8'),
                (7, '7'),
                (6, '6'),
                (5, '5'),
                (4, '4'),
                (3, '3'),
                (2, '2'),
                (1, '1'),
            )

    def queryset(self, request, queryset):
        
        if self.value() is None:
            return queryset
        elif int(self.value()) in range(32):
            return queryset.filter(startt__2 = int(self.value()))

class HasdebitFilter(admin.SimpleListFilter):
    template = 'django_admin_listfilter_dropdown/dropdown_filter.html'
    title = 'وضعیت معوق'
    parameter_name = 'has_debit_amount'
    def lookups(self, request, model_admin):
            return (
                (1, 'آری'),
                (0, 'خیر')
            )
    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(debit_amount__gt = 0)
        elif self.value() == '0':
            return queryset.filter(debit_amount__lte = 0)
        return queryset

class BusyVccAdmin(admin.ModelAdmin):
    fieldsets_and_inlines_order = ()
    formfield_overrides = {
        models.IntegerField : { 'widget' : NumberInput(attrs={'size' : 40})}
    }
    inlines = [PaymentInline]
    search_fields = ( 'number', 'contract__customer_fullname')
    list_filter = [dayFilter,debitFilter,HasdebitFilter,('contract__supplier__name', DropdownFilter),('coffer__name', DropdownFilter),statusFilter,contract_statusFilter,]
    list_display = ['name','customer_mobile','face_pays','number_of_debit' ,'debit_amount','number','instalment_amount','number_of_instalments','supplier_name', 'startt_change'
                    ,'last_pay_date']
    readonly_fields = ['penalty_amount','pay_status', 'jinstalment_date','last_pay_date','number_of_pays' ,'face_pays'  ,'number_of_debit','instalment_amount','contract_customer'
                            ,'debit_amount', 'contract_link', 'startt','con_last_pay','birth_day','tot_debit','phone_number',
                            'fam_mobile', 'cont_status', 'fam_hmobile', 'income', 'job', 'customer_mobile', 
                            'job_address', 'final_debit', 'total_amount', 'contract_id', 'emerge1_number', 'con_first_pay', 'family', 'home_type',
                            'remaining_amount', 'contract_coffer', 'con_number_ins', 'job_phone','con_supp',
                            'fam_hmobile_1', 'family_1', 'home_type_1', 'fam_mobile_1', 'surety1_mobile_number', 'surety1_job_address',
                            'surety1_name', 's_1_emerge1_number', 'surety1_job_phone_number', 'surety1_phone_number', 'birth_day_1', 'surety1_job',
                            'surety1_estimate_income','surety2_job', 'surety2_job_phone_number', 'surety2_mobile_number', 'home_type_2', 's_2_emerge1_number',
                            'surety2_estimate_income', 'birth_day_2', 'surety2_name', 'fam_hmobile_2', 'surety2_phone_number', 'fam_mobile_2', 'surety2_job_address',
                            'family_2' ]
   
    actions = ['export_as_excel','update','make_free']
    fieldsets = (
        ('متقاضی' , {
            'fields' : (('contract_customer','customer_mobile','phone_number','emerge1_number'),('job','income','home_type', 'birth_day'),('job_address','job_phone',)
                        ,('family','fam_mobile','fam_hmobile'))
        }),
        ('ضامن اول' , {
            'fields' : (('surety1_name','surety1_mobile_number','surety1_phone_number','s_1_emerge1_number'),('surety1_job','surety1_estimate_income','home_type_1','birth_day_1'),('surety1_job_address','surety1_job_phone_number')
                        ,('family_1','fam_mobile_1','fam_hmobile_1'))
        }),
        ('ضامن دوم' , {
            'fields' : (('surety2_name','surety2_mobile_number','surety2_phone_number','s_2_emerge1_number',),('surety2_job','surety2_estimate_income','home_type_2','birth_day_2')
                        ,('surety2_job_address','surety2_job_phone_number'),('family_2','fam_mobile_2','fam_hmobile_2'))
        }),
        ('قرارداد' , {
            'fields' : (('contract_id','cont_status','contract_coffer','con_supp','instalment_amount','con_number_ins','total_amount'),('con_first_pay','number_of_pays','con_last_pay','pay_status',))
        }),
        ('کارت' , {
            'fields' : (('number','amount','face_pays','number_of_debit','debit_amount'),('new_status','penalty_amount','remaining_amount','tot_debit','final_debit',))
        })
    )
    def get_fieldsets(self, request, obj=None):
        
        try:
            self.surety1 = obj.contract.suretys.get(order='1').surt
            
        except:
            self.surety1 = ''
            
        try:
            self.familyy_1 = Family.objects.get(customer = self.surety1)
        except:
            self.familyy_1 = ''
        try:
            self.surety2 = obj.contract.suretys.get(order='2').surt
            
        except:
            self.surety2 = ''
        try:
            self.familyy_2 = Family.objects.get(customer = self.surety2)
        except:
            self.familyy_2 = ''
        
        try:
            self.familyy = Family.objects.get(customer = obj.contract.customer)
        except:
            self.familyy = ''
        fields = super(busyVccAdmin, self).get_fieldsets(request, obj)

        x = fields
        if self.surety1 == '':
            x = x[:1] + x[3:]
        elif self.surety2 == '':
            x = x[:2] + x[3:]

        return x
    def get_list_filter(self, request):
        list_filter = super().get_list_filter(request)
        if 'contract.افراد حقوقی' in request.user.get_all_permissions() and not request.user.is_superuser:
            list_filter = ()
        else:
            pass
        return list_filter
    def get_actions(self, request):
        actions = super().get_actions(request)
        
        if 'contract.افراد حقوقی' in request.user.get_all_permissions() and not request.user.is_superuser:
            
            actions = ()
        else:
            pass
        return actions
    
    def get_queryset(self,request):
        queryset = super().get_queryset(request)
        if 'contract.افراد حقوقی' in request.user.get_all_permissions() and not request.user.is_superuser:
            queryset = queryset.filter(status__in=['1','2'],contract__status='6') 
        else:
            queryset = queryset.filter(status__in=['1','2'])
        
        dtoday = jdatetime.date.today().day
        mtoday = jdatetime.date.today().month
        ytoday = jdatetime.date.today().year
        queryset = queryset.annotate(
            yyy = Case(
                When(startt__0=1300,then=-2),
                default= ytoday - (F('startt__0') + 1 ) ,
                output_field=IntegerField()
            )
        ).annotate(
            yearr = Case(
                When(yyy__gt = -2,then= F('yyy')*12 + (13 - F('startt__1')) + (mtoday-1)),
                When(yyy = -2, then= None),
                output_field=IntegerField()), 
            dayy = Case(
                When(startt__2__lte=dtoday,then=1),
                default= 0,
                output_field=IntegerField(),
            )).annotate(
            instalment_date = Case(
                When(contract__sign_date__isnull=True,then=date(1300,1,1)),
                default= F('contract__sign_date'),
                output_field=DateField()
            ),
            number_of_pays = Count('payment'),
            total = Sum('payment__amount'),
            last_pay_date_null = Max('payment__date'),
            first_pay_date = Min('payment__date'),
            number_of_instalment = F('contract__number_of_instalment'),
            ddate =F('yearr'),
            
            face_pays_months = ExpressionWrapper(F('dayy')  + F('yearr') ,output_field = IntegerField()),
        ).annotate(
            last_pay_date = Case(
                When(last_pay_date_null__isnull=True,then=date(1,1,1)),
                default= F('last_pay_date_null'),
                output_field=DateField()
            ),
            face_pays = Case(
                When(face_pays_months__gt=F('number_of_instalment'),then= F('number_of_instalment')),
                When(face_pays_months__isnull=True,then=0),
                default=F('face_pays_months') - Value(0),
                output_field=IntegerField()
            ),
        ).annotate(
            debit_amount = Case(
                When(total__isnull=False,then=F('instalment_amount')*F('face_pays') - F('total')),
                default= F('instalment_amount')*F('face_pays'),
                output_field=FloatField()
            )
        ).annotate(
            number_of_debit = Case(
                When(contract__isnull = True,then = -24),
                default=  (F('debit_amount') / Cast(F('instalment_amount'),FloatField())),
                output_field=FloatField()
            )
        ).order_by('-number_of_debit')
        return queryset

    def name(self,obj):
        try:
            return obj.contract.customer
        except:
            return VCC_STATUSES[obj.status]
    name.short_description = 'نام متقاضی' 
    def contract_customer(self , obj):
        try:
            display_text = "<center><a href='/admin/customer/customer/{}/change' target='_blank'>{}</a></center>".format(obj.contract.customer.pk,obj.contract.customer)
            return format_html(display_text)
        except:
            return VCC_STATUSES[obj.status]
    contract_customer.short_description = 'نام متقاضی' 
    def contract_link(self , obj):
        try:
            display_text = "<center><a href='/admin/contract/contract/{}/change' target='_blank'>{}</a></center>".format(obj.contract.pk,obj.contract)
            return format_html(display_text)
        except:
            return VCC_STATUSES[obj.status]
    contract_link.short_description = 'قرارداد' 
    def customer_mobile(self , obj):
        try:        
            return obj.contract.customer.mobile_number
        except:
            return ''
    customer_mobile.short_description = 'شماره همراه'
    
    def face_pays(self , obj):
        try: 
            return persian_numbers_converter(obj.face_pays)
        except:
            return ''
    face_pays.short_description = 'سررسید'
    
    def phone_number(self , obj):
        try:
            return obj.contract.customer.user.phone_number
        except:
            return ''
    phone_number.short_description = 'شماره ثابت'
    def emerge1_number(self , obj):
        try:
            return obj.contract.customer.user.workplace_number
        except:
            return ''
    emerge1_number.short_description = 'شماره ضروری'
    def supplier_name(self , obj):
        try:
            return obj.contract.supplier_name
        except:
            return ''
    supplier_name.short_description = 'تامین کننده'
    def jinstalment_date(self,obj):
        return obj.contract.jinstalment_start_date
    jinstalment_date.short_description = 'روز سررسید'
    jinstalment_date.admin_order_field = 'instalment_date'
    
    def last_pay_date(self,obj):
        if obj.last_pay_date_null != None:
            return persian_numbers_converter(jalali.Gregorian(obj.last_pay_date_null).persian_string('{}/{}/{}'))
        else:
            return ''
    last_pay_date.short_description = 'آخرین پرداخت'
    last_pay_date.admin_order_field = 'last_pay_date'

    def instalment_amount(self,obj):
        return obj.contract.instalment_amount_persian
    instalment_amount.short_description = 'قسط'
    instalment_amount.admin_order_field = 'instalment_amount'

    def number_of_instalments(self,obj):
        return obj.number_of_instalment
    number_of_instalments.short_description = 'اقساط'

    def number_of_pays(self,obj):
        return persian_numbers_converter(obj.number_of_pays)
    number_of_pays.short_description = 'تعداد پرداخت ها'
    number_of_pays.admin_order_field = 'number_of_pays'

    def number_of_debit(self,obj):
        return persian_numbers_converter(round(obj.number_of_debit,1)) 
    number_of_debit.short_description = 'معوق'
    number_of_debit.admin_order_field = 'number_of_debit'

    def debit_amount(self,obj):
        return persian_numbers_converter(int(obj.debit_amount), 'price') 
    debit_amount.short_description = 'مبلغ معوق'
    debit_amount.admin_order_field = 'debit_amount'

    def penalty_amount(self,obj):
        return persian_numbers_converter(obj.contract.instalment_detail[0], 'price') 
    penalty_amount.short_description = 'مبلغ جریمه'

    def pay_status(self,obj):
        return PAY_STATUS_DICT[obj.contract.instalment_detail[1]]
    pay_status.short_description = 'وضعیت پرداخت'

    def job(self , obj):
        return obj.contract.customer.job
    job.short_description = 'عنوان شغل'
    def birth_day(self,obj):
        if obj.contract.customer.birth_date is not None:
            return persian_numbers_converter( jalali.Gregorian(obj.contract.customer.birth_date).persian_string('{}/{}/{}') )
    birth_day.short_description = 'تاریخ تولد' 

    def birth_day_1(self,obj):
        
        if self.surety1.birth_date is not None:
            return persian_numbers_converter( jalali.Gregorian(self.surety1.birth_date).persian_string('{}/{}/{}') )
    birth_day_1.short_description = 'تاریخ تولد' 

    def birth_day_2(self,obj):
        
        if self.surety2.birth_date is not None:
            return persian_numbers_converter( jalali.Gregorian(self.surety2.birth_date).persian_string('{}/{}/{}') )
    birth_day_2.short_description = 'تاریخ تولد' 
    def income(self,obj):
        return obj.income
    income.short_description = 'درآمد ماهیانه'
    
    def surety2_name(self,obj):
        return self.surety2.first_name +' ' +self.surety2.last_name
    surety2_name.short_description = 'نام ضامن دوم'

    def surety1_phone_number(self,obj):
        return self.surety1.phone_number
    surety1_phone_number.short_description = 'شماره همراه'

    def surety2_phone_number(self,obj):
        return self.surety2.phone_number
    surety2_phone_number.short_description = 'شماره همراه اقوام'

    def surety1_phone_number(self,obj):
        return self.surety1.phone_number
    surety1_phone_number.short_description = 'شماره ثابت'

    def surety2_phone_number(self,obj):
        return self.surety2.phone_number
    surety2_phone_number.short_description = 'شماره ثابت'

    def surety2_mobile_number(self,obj):
        return self.surety2.mobile_number
    surety2_mobile_number.short_description = 'شماره همراه'

    def surety1_mobile_number(self,obj):
        return self.surety1.mobile_number
    surety1_mobile_number.short_description = 'شماره همراه'

    def surety2_job(self,obj):
        return self.surety2.job
    surety2_job.short_description = 'عنوان شغل'

    def surety1_job(self,obj):
        return self.surety1.job
    surety1_job.short_description = 'عنوان شغل'

    def surety2_estimate_income(self,obj):
        return self.surety2.estimate_income
    surety2_estimate_income.short_description = 'درآمد ماهیانه'

    def surety1_estimate_income(self,obj):
        return self.surety1.estimate_income
    surety1_estimate_income.short_description = 'درآمد ماهیانه'

    def surety2_job_phone_number(self,obj):
        return self.surety2.job_phone_number
    surety2_job_phone_number.short_description = ' شماره تماس محل کار'

    def surety1_job_phone_number(self,obj):
        return self.surety1.job_phone_number
    surety1_job_phone_number.short_description = 'شماره تماس محل کار'

    def surety2_job_address(self,obj):
        return self.surety2.job_address
    surety2_job_address.short_description = ' آدرس محل کار'

    def surety1_job_address(self,obj):
        return self.surety1.job_address
    surety1_job_address.short_description = 'آدرس محل کار'

    def tot_debit(self,obj):
        return persian_numbers_converter(obj.contract.debit_amount(), 'price') 
    tot_debit.short_description = 'بدهی کل'

    def remaining_amount(self,obj):
        x = obj.contract.remaining_amount()
        return persian_numbers_converter(x, 'price') 
    remaining_amount.short_description = 'مبلغ باقیمانده'
    def final_debit(self,obj):
        x = obj.contract.remaining_amount() + obj.contract.instalment_detail[0]
        return persian_numbers_converter(x, 'price') 
    final_debit.short_description = 'مبلغ جهت تسویه نهایی'
    def home_type(self,obj):
        return HOME_TYPE[obj.contract.customer.home_type]
    home_type.short_description = 'وضعیت سکونت'
    def home_type_1(self,obj):
        return HOME_TYPE[self.surety1.home_type]
    home_type_1.short_description = 'وضعیت سکونت'
    def home_type_2(self,obj):
        return HOME_TYPE[self.surety2.home_type]
    home_type_2.short_description = 'وضعیت سکونت'
    def job_phone(self,obj):
        return obj.contract.customer.job_phone
    job_phone.short_description = 'شماره تماس محل کار'
    def job_address(self,obj):
        return obj.contract.customer.job_address
    job_address.short_description = 'آدرس محل کار'
    def family(self,obj):
        return self.familyy
    family.short_description = 'اقوام درجه یک'

    def family_1(self,obj):
        return self.familyy_1
    family_1.short_description = 'اقوام درجه یک'

    def family_2(self,obj):
        return self.familyy_2
    family_2.short_description = 'اقوام درجه یک'
    def fam_mobile(self,obj):
        return self.familyy.mobile_number
    fam_mobile.short_description = 'شماره  همراه اقوام '

    def fam_hmobile(self,obj):
        return self.familyy.phone_number
    fam_hmobile.short_description = 'شماره  ثابت اقوام '

    def fam_mobile_1(self,obj):
        return self.familyy_1.mobile_number
    fam_mobile_1.short_description = 'شماره  همراه اقوام '

    def fam_hmobile_1(self,obj):
        return self.familyy_1.phone_number
    fam_hmobile_1.short_description = 'شماره  ثابت اقوام '
    def fam_mobile_2(self,obj):
        return self.familyy_2.mobile_number
    fam_mobile_2.short_description = 'شماره  همراه اقوام '
    def contract_id(self,obj):
        return obj.contract_id
    contract_id.short_description = 'شناسه قرارداد' 
    def cont_status(self,obj):
        return CONTRACT_STAT_D[obj.contract.status]
    cont_status.short_description = 'وضعیت قرارداد'
    def contract_coffer(self,obj):
        return obj.contract.coffer
    contract_coffer.short_description = 'تامین مالی' 
    def con_supp(self,obj):
        return obj.contract.supplier.name
    con_supp.short_description = 'تامین کننده' 
    def con_number_ins(self,obj):
        return obj.contract.number_of_instalments
    con_number_ins.short_description = 'اقساط' 
    def total_amount(self,obj):
        x = obj.instalment_amount * obj.contract.number_of_instalments 
        return persian_numbers_converter(x, 'price') 
    total_amount.short_description = 'مبلغ کل اقساط'
    def con_last_pay(self,obj):
        if obj.last_pay_date is not None:
            return persian_numbers_converter( jalali.Gregorian(obj.last_pay_date).persian_string('{}/{}/{}') )
    con_last_pay.short_description = 'تاریخ اخرین پرداخت'
    def con_first_pay(self,obj):
        if obj.first_pay_date is not None:
            return persian_numbers_converter( jalali.Gregorian(obj.first_pay_date).persian_string('{}/{}/{}') )
    con_first_pay.short_description = 'تاریخ  اولین پرداخت'
    def startt_change(self,obj):
        try:
            x =list(obj.startt)
            return "/".join(str(y) for y in x)
        except:
            return ""
    startt_change.short_description = 'روز سررسید'
    def surety1_name(self,obj):
        return self.surety1.first_name +' ' +self.surety1.last_name
    surety1_name.short_description = 'نام ضامن اول'
    def s_1_emerge1_number(self , obj):
        try:
            return self.surety1.user.workplace_number
        except:
            return ''
    s_1_emerge1_number.short_description = 'شماره ضروری'

    def s_2_emerge1_number(self , obj):
        try:
            return self.surety2.user.workplace_number
        except:
            return ''
    s_2_emerge1_number.short_description = 'شماره ضروری'
    def fam_hmobile_2(self,obj):
        return self.familyy_2.phone_number
    fam_hmobile_2.short_description = 'شماره تماس ثابت اقوام '

    def update(modeladmin,request,queryset):
        for v in queryset:
            debit = round(v.contract.debit_amount() / v.contract.instalment_amount , 1) 
            if debit < 2:
                v.new_status = '1'
            elif debit > 3:
                v.new_status = '2'
            pays = payment.objects.filter(VCC = v)
            total_amount = 0
            for p in pays:
                total_amount += p.amount
            v.amount = total_amount
            v.save()
    update.short_description = 'به روز رسانی موجودی کارت های انتخاب شده'

    def make_free(modeladmin,request,queryset):
        for v in queryset:
            if v.status == '1':
                v.status = '0'
                v.save()
    make_free.short_description = 'آزاد کردن کارت های انتخاب شده'

    def export_as_excel(modeladmin, request, queryset):
        init_row = ['ردیف','شماره کارت','موجودی']
        workbook = xlsxwriter.Workbook("vccs_excel.xlsx")
        cell_format = workbook.add_format({'num_format': '#,###'})
        cell_format.set_align('center')
        cell_format.set_align('vcenter')
        cell_format.set_font_name('B Nazanin')
        worksheet = workbook.add_worksheet()
        worksheet.right_to_left()
        row = 0
        col = 0
        worksheet.set_column(1 , 3 , 20 , cell_format)
        for data in init_row:
            worksheet.write(row, col , data)
            col += 1
        row += 1
        col = 0
        for v in queryset:
            col = 0
            worksheet.write(row , col , row)
            col += 1
            worksheet.write(row , col , v.number)
            col += 1
            worksheet.write(row , col , v.amount)
            row += 1
        workbook.close() 
        return FileResponse(open("vccs_excel.xlsx",'rb'),as_attachment = True)
    export_as_excel.short_description = 'خروجی اکسل کارت های انتخاب شده'

class Vcc_freeAdmin(admin.ModelAdmin):
    fieldsets_and_inlines_order = ()
    search_fields = ('number',)
    list_filter = [ 'coffer',]
    list_display = ['__str__','coffer']
    actions = ['export_as_excel']
    def export_as_excel(modeladmin, request, queryset):
        init_row = ['ردیف','شماره کارت','صندوق']
        workbook = xlsxwriter.Workbook("vccs_excel.xlsx")
        cell_format = workbook.add_format({'num_format': '#,###'})
        cell_format.set_align('center')
        cell_format.set_align('vcenter')
        cell_format.set_font_name('B Nazanin')
        worksheet = workbook.add_worksheet()
        worksheet.right_to_left()
        row = 0
        col = 0
        worksheet.set_column(1 , 3 , 20 , cell_format)
        for data in init_row:
            worksheet.write(row, col , data)
            col += 1
        row += 1
        col = 0
        for v in queryset:
            col = 0
            worksheet.write(row , col , row)
            col += 1
            worksheet.write(row , col , v.number)
            col += 1
            worksheet.write(row , col , v.coffer.name)
            row += 1
        workbook.close() 
        return FileResponse(open("vccs_excel.xlsx",'rb'),as_attachment = True)
    export_as_excel.short_description = 'خروجی اکسل کارت های انتخاب شده'


CONTRACT_STAT_D = {
        '0' : 'تایید دریافت پیش پرداخت',
        '1' : 'درحال عقد قرارداد',
        '2' : ' تایید قرارداد و ارسال کالا',
        '3' : 'تسویه با فروشگاه',
        '4' : 'پرداخت اقساط توسط متقاضی',
        '5' : 'تسویه متقاضی و تحویل مدارک',
        '6' : 'نکول قطعی',
        '7' : 'انصراف متقاضی',
        }

class Duration_contractAdmin(contractAdmin):
    readonly_fields = ('customer_fullname','customer_level','supplier_name', 'vcc_number', 'jcontract_permission_date','new_vccc','ptotal_amount_of_instalments',
                       'pcustomer_check','psurety_check','ploan_face_value','ploan_amount','psupplier_balance','pcompany_gain','pwarranty_gain','pinvestor_gain',
                       'ptotal_amount', 'ppure_gain','ptotal_company_gain',
                       'customer_melli_code','customer_birth_date','customer_marital_status','customer_address','customer_postal_code','customer_phone_number',
                       'customer_home_type','customer_home_owner','customer_father', 'customer_mobile','customer_status','customer_credit_rank','customer_description',
                       'customer_job_class','customer_job_status','customer_job','customer_estimate_income','customer_job_phone_number','customer_job_address',
                       'surety1_full_name','surety1_father','surety1_melli_code','surety1_mobile','surety1_birth_date','surety1_marital_status','surety1_address','surety1_postal_code','surety1_phone_number',
                       'surety1_home_type','surety1_home_owner','surety1_job_class','surety1_job_status','surety1_job','surety1_estimate_income','surety1_job_phone_number','surety1_job_address',
                       'surety2_full_name','surety2_father','surety2_melli_code','surety2_mobile','surety2_birth_date','surety2_marital_status','surety2_address','surety2_postal_code','surety2_phone_number',
                       'surety2_home_type','surety2_home_owner','surety2_job_class','surety2_job_status','surety2_job','surety2_estimate_income','surety2_job_phone_number','surety2_job_address','check_date_str')
    fieldsets = (
        ('اطلاعات عمومی اقساط' , {
            'fields' : (('customer','customer_mobile'),('vcc_free','new_vccc'),'contract_id','status','sign_date' ,'start_date_ins','amount_of_installment',
                        'duration','number_of_instalment' ,'ptotal_amount_of_instalments',('customer_check_factor' ,'pcustomer_check')
                        ,('surety_check_factor','psurety_check'))
        }),
        ('اطلاعات فاکتور و تامین کننده' , {
             'fields' : ('supplier','net_amount' ,'face_net_amount','ploan_face_value' ,'downpayment','ploan_amount','psupplier_balance','clearing_date'
             ,'discount','ptotal_amount')
        }),
        ('اطلاعات حسابداری' , {
            'fields' : (('company_gain_rate','pcompany_gain'),('warranty_gain_rate' ,'share_rate','pwarranty_gain'),('investor_gain_rate','pinvestor_gain'),
             'ppure_gain','ptotal_company_gain','financial_source_rate','check_date_str',)
        }),
        ('متقاضی' , {
            'fields' : (('customer_fullname','customer_father','customer_melli_code','customer_birth_date','customer_marital_status','customer_address','customer_postal_code','customer_phone_number',),
                        ('customer_home_type','customer_home_owner',),('customer_job_class','customer_job_status','customer_job','customer_estimate_income','customer_job_phone_number','customer_job_address'))
        }),
        ('ضامن اول' , {
            'fields' : (('surety1_full_name','surety1_father','surety1_melli_code','surety1_mobile','surety1_birth_date','surety1_marital_status','surety1_address','surety1_postal_code','surety1_phone_number',),
                        ('surety1_home_type','surety1_home_owner',),('surety1_job_class','surety1_job_status','surety1_job','surety1_estimate_income','surety1_job_phone_number','surety1_job_address'))
        }),
        ('ضامن دوم' , {
            'fields' : (('surety2_full_name','surety2_father','surety2_melli_code','surety2_mobile','surety2_birth_date','surety2_marital_status','surety2_address','surety2_postal_code','surety2_phone_number',),
                        ('surety2_home_type','surety2_home_owner',),('surety2_job_class','surety2_job_status','surety2_job','surety2_estimate_income','surety2_job_phone_number','surety2_job_address'))
        }),
        ('اطلاعات اعتبارسنجی' , {
            'fields' : ('customer_status','customer_level','jcontract_permission_date','customer_credit_rank','customer_description')
        }),  
        ('متفرقه' , {
            'fields' : ('coffer' , 'issuer' ,'Type'  ,'invoice_date' , 'invoice_number' ,'description' ,'send_to_coffer' ,'appoint_time')
        }),
        ('پیامک' , {
            'fields' : ('sms_send',)
        }),
    )


admin.site.register(contract , contractAdmin)
admin.site.register(Duration_contract , Duration_contractAdmin)
admin.site.register(payment , paymentAdmin)
admin.site.register(vcc_free,vcc_freeAdmin)
admin.site.register(vcc,busyVccAdmin)

