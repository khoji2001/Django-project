
from OTP.models import select_MessageText
from supplier.models import supplier
from django.contrib import admin
from .models import *
from .forms import CustomerForm, CustomerCreationForm
from django_admin_listfilter_dropdown.filters import DropdownFilter,ChoiceDropdownFilter
import xlsxwriter
from django.utils.html import format_html
from django.db import models
from django.forms import NumberInput,Textarea
from django.http import FileResponse
from document.admin import CustomerDocumentInline
from contract.admin import ContractBriefInline,ContractInline,SuretysInline
from contract.models import CONTRACT_STATUSES, contract
from customer.models import CUSTOMER_STATUS
from jalali_date.admin import ModelAdminJalaliMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
import jdatetime
import pytz 
import os
from django.conf import settings
con_status_di = {
    '0' : 'تایید دریافت پیش پرداخت',
    '1' : 'درحال عقد قرارداد',
    '2' : ' تایید قرارداد و ارسال کالا',
    '3' : 'تسویه با فروشگاه',
    '4' : 'پرداخت اقساط توسط متقاضی',
    '5' : 'تسویه متقاضی و تحویل مدارک',
    '6' : 'نکول قطعی',
    '7' : 'انصراف متقاضی'
}

PAY_STATUS_DICT = {
    '1' : 'خوش حساب',
    '2' : 'پرداخت نامنظم',
    '3' : 'پرداخت پرخطر',
    '4' : 'بدحساب'
}

CUSTOMER_STATUS = CUSTOMER_STATUS + (('7' , 'پرداخت اقساط'),)
CUSTOMER_STATUS_DICTIONARY = dict((x, y) for x, y in CUSTOMER_STATUS)

# Register your models here.
class FinancialInformationInline(admin.StackedInline):
    model = Financial_Information
    extra = 0

class CheckInformationInline(admin.StackedInline):
    model = Check_information
    extra = 0

class FamilyInline(admin.StackedInline):
    model = Family
    extra = 0
    verbose_name = 'اطلاعات اقوام درجه یک'
    verbose_name_plural = 'اطلاعات اقوام درجه یک'
    fieldsets = (
        ( None , {
            'fields': ('Type', 'first_name', 'last_name', 'mobile_number', 'melli_code', 'phone_number', 'phone_number_description')
        }),
    )

class SuretiesInline(admin.StackedInline):
    model = Guarantee
    extra = 0 
    fk_name = 'customer'
    verbose_name = 'ضامن'
    verbose_name_plural = 'ضامن ها'
    fieldsets = (
    (None , {
            'fields': (('surety', 'surety_order'),)
        }),
    )

class CustomersInline(admin.StackedInline):
    model = Guarantee
    extra = 0 
    fk_name = 'surety'
    verbose_name = 'ضمانت شده'
    verbose_name_plural = 'ضمانت شده ها'
    fieldsets = (
    (None, {
            'fields': (('customer', 'surety_order'),)
        }),
    )

class PersonalHomeInline(admin.StackedInline):
    model = PersonalHome
    extra = 0
class OrganizationHomeInline(admin.StackedInline):
    model = OrganizationHome
    extra = 0
class RentalHomeInline(ModelAdminJalaliMixin, admin.StackedInline):
    model = RentalHome
    extra = 0
class SupplierInline(admin.StackedInline):
    model = supplier.customer.through
    verbose_name = "تامین کننده"
    verbose_name_plural = "تامین کننده ها"
    extra = 0
class SuretyInline(admin.StackedInline):
    model = surety
    readonly_fields = ['document' , 'credit_rank','mellicard','full_address']
    extra = 0
    formfield_overrides = {
        models.IntegerField : { 'widget' : NumberInput(attrs={'size' : 40})}
    }
    ordering = ['id']
    fieldsets = (
        (None , {
            'fields' : ('first_name','last_name','father_name','melli_code','mobile_number','phone_number','workplace_number',('province','city','address')
                    ,'postal_code','estimate_income',('job_class','job'),('mellicard','credit_rank','document'))
        }),
    )
    def document(self,obj):
        try:
            document_id = obj.surety_document.pk
            return format_html("<a href='/admin/document/surety_document/{}/change/' target='_blank'><b>{}</b></a>".format(document_id , 'سایر مدارک'))
        except:
            return 'ندارد'
    document.short_description = 'مدارک ضامن'

    def credit_rank(self,obj):
        try:
            ice = obj.surety_document.credit_rate
            display_text = "<a href='{}' target='_blank'><b>{}</b></a>".format(ice.url , "رتبه اعتباری")
            return format_html(display_text)
        except:
            return 'ندارد'
    credit_rank.short_description = 'رتبه اعتباری ضامن'
    def mellicard(self,obj):
        try:
            mellicard = obj.surety_document.mellicard_front
            display_text = "<a href='{}' target='_blank'><b>{}</b></a>".format(mellicard.url , "کارت ملی")
            return format_html(display_text)
        except:
            return 'ندارد'
    mellicard.short_description = 'کارت ملی ضامن'

class ContractStatusFilter(admin.SimpleListFilter):
    template = 'django_admin_listfilter_dropdown/dropdown_filter.html'
    title = _('وضعیت قراردادی')
    parameter_name = 'contract__status'
    def lookups(self, request, model_admin):
        return [c for c in CONTRACT_STATUSES] + [('9','بدون قرارداد')]
    def queryset(self, request, queryset):
        if self.value() == '9':
            return queryset.filter(contract__isnull = True)
        elif self.value() != None:
            return queryset.filter(contract__status = self.value()) 

class UserFilter(admin.SimpleListFilter):
    title = _('کاربر')
    parameter_name = 'user_type'

    def __init__(self, *args, **kwargs):
        super(UserFilter, self).__init__(*args, **kwargs)

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': _('متقاضی'),
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == str(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('1', _('ضامن')),
            ('2', _('همه')),
        )
    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        sureties_id = Guarantee.objects.values_list('surety',flat=True)
        a1 = set(customer.objects.values_list('id',flat=True)) - set(sureties_id)
        output = set.union(a1 , set (contract.objects.values_list('customer',flat=True)))
        
        if self.value() == None:
            return queryset.filter(id__in = output)
        if self.value() == '1':
            return queryset.filter(id__in = sureties_id)
        if self.value() == '2':
            return queryset
        

class CustomerAdmin(ModelAdminJalaliMixin, UserAdmin):
    change_form_template = 'admin/customer/change_form.html'
    add_form_template = 'admin/customer/change_form.html'
    add_form = CustomerCreationForm
    form = CustomerForm
    formfield_overrides = {
        models.IntegerField : { 'widget' : NumberInput(attrs={'size' : 40})}
    }
    inlines = [FamilyInline ,PersonalHomeInline,RentalHomeInline, OrganizationHomeInline, financialInformationInline, checkInformationInline , CustomerDocumentInline, suretiesInline, customersInline, ContractBriefInline, ContractInline,AppointInline, SupplierInline]
    ordering = ['-date_joined']
    readonly_fields = ['full_address' , 'far_status','suppliers','customer_mellicard','customer_ice','customer_otherdoc' ]
    list_display = ('user','all_doc', 'customer_status','customer_type', 'con_status' ,'payment_status','instalment_start_date','jdate_joined','level' ,'user_document', 'job' , 'pestimate_income' 
                , 'suretys' , 'customer_ice' , 'suretys_ice' ,'active_contracts' ,'card_number', 'clear_contracts'
                , 'instalment' , 'suppliers','customer_file')
    list_filter = (('status',ChoiceDropdownFilter),('level',ChoiceDropdownFilter), ('supplier__name',DropdownFilter) ,ContractStatusFilter, UserFilter)
    search_fields = ('last_name','first_name','melli_code','mobile_number')
    autocomplete_fields = ['user']
    fieldsets = (
        ('اطلاعات کاربری', {
            'fields': ('melli_code', 'mobile_number', 'password') }),
        ('اطلاعات هویتی', {
            'fields' :('first_name' ,'last_name' ,'father_name', 'gender', 'education', 'birth_date', 'phone_number', 'phone_number_description'
            , 'workplace_number', 'marital_status') }),
        ('اطلاعات سکونتی', {
            'fields' :('province', 'city', 'address', 'postal_code') }),
        ('اطلاعات شغلی', {
            'fields' : ('job_class','job_status','job', 'job_workplace', 'job_phone_number', 'job_address', 'estimate_income')                   
        }),
        ('اطلاعات قراردادی', {
            'fields' : ('suppliers', 'level')
        }),
        ('اطلاعات اعتبارسنجی', {
            'fields' : (('status','confirmation_date', 'far_status'),('fileـsender' , 'credit_rating_score' ,'credit_rating_description','credit_date',)
                        ,('accept_reason','accept_desc'),('faultdocument_reason','faultdocument_desc'),('expire_reason','expire_desc'),('cancel_reason','cancel_desc'),('reject_reason','reject_desc')
                        ,'credit_rank','cust_description', 'description', 'organ_code', 'organ', 'customer_ice', 'customer_otherdoc', 'surety_permission', 'again_purchase', 'surety_date')
        }),
        ('پیامک', {
            'fields': ('sms_send',)
        }),
    )
    add_fieldsets = (
        ('اطلاعات کاربری', {
            'classes': ('wide',),
            'fields': ('melli_code','mobile_number', 'password1', 'password2')}
        ),
        ('اطلاعات هویتی', {
            'fields' :('first_name' ,'last_name' ,'father_name', 'gender', 'education', 'birth_date', 'phone_number', 'phone_number_description'
            , 'workplace_number', 'marital_status') }),
        ('اطلاعات سکونتی', {
            'fields' :('province', 'city', 'address', 'postal_code') }),
        ('اطلاعات شغلی', {
            'fields' : ('job_class','job_status','job', 'job_workplace', 'job_phone_number', 'job_address', 'estimate_income')                   
        }),
        ('اطلاعات قراردادی', {
            'fields' : ('suppliers', 'level')
        }),
        ('اطلاعات اعتبارسنجی', {
            'fields' : ('status', 'credit_rank','cust_description', 'description', 'organ_code', 'organ', 'customer_ice', 'customer_otherdoc', 'surety_permission', 'again_purchase')
        }),
        (None, {
            'fields': ('')
        }),
    )
    fieldsets_and_inlines_order = ('f', 'f','i', 'f', 'i', 'i','i', 'f', 'f','i', 'i', 'f', 'i', 'i','i','i','i','i','i','f')
    def delete_select(self, request, obj):
        for o in obj.all():
            o.delete()
    delete_select.short_description = 'حذف مقتقاضی همراه با حذف کاربر'
    actions = ['delete_select','export_as_excel','set_to_cancel','set_to_expired','update']
    def payment_status(self,obj):
        x = contract.objects.filter(customer = obj).last()
        try:
            return PAY_STATUS_DICT[x.instalment_detail[1]]
        except:
            return ''
    payment_status.short_description = 'وضعیت پرداخت'

    def instalment_start_date(self,obj):
        x = contract.objects.filter(customer = obj).last()
        try:
            return x.jinstalment_start_date
        except:
            return ''
    instalment_start_date.short_description = 'تاریخ اولین قسط'

    def con_status(self,obj):
        x = contract.objects.filter(customer = obj).last()
        try:
            return con_status_di[x.status]
        except:
            return ''
    con_status.short_description = 'وضعیت قرارداد'
    
    def jdate_joined(self,obj):
        try:
            return persian_numbers_converter(jalali.Gregorian(obj.user.date_joined.date()).persian_string('{}/{}/{}'))
        except:
            return 'تاریخ معتبر نیست'
    jdate_joined.short_description = 'تاریخ ثبت نام'
    def pestimate_income(self,obj):
        return persian_numbers_converter(obj.estimate_income , 'price')
    pestimate_income.short_description = format_html('<p> حدود درآمد ماهانه</p><p>(میلیون ریال)</p>')
    pestimate_income.admin_order_field = 'estimate_income'

    def customer_type(self,obj):
        sur = Guarantee.objects.filter(surety = obj).count()
        cust = contract.objects.filter(customer = obj).count()
        if sur>0 and cust>0:
            return 'متقاضی و ضامن'
        elif sur>0:
            return 'ضامن'
        elif cust>0:
            return 'متقاضی'
        else:
            return 'بدون قرارداد'
    customer_type.short_description = 'نوع متقاضی'


    def customer_status(self,obj):
        stat = obj.status
        if obj.status == '1'and len(contract.objects.filter(customer = obj , status='4')) > 0:
            stat = '7'
        return CUSTOMER_STATUS_DICTIONARY[f'{stat}']      
    customer_status.short_description ='وضعیت متقاضی'



    def user_document(self,obj):
        try:
            document_id = obj.customer_document.pk
            return format_html("<a href='/admin/document/customer_document/{}/change/' target='_blank'><b>{}</b></a>".format(document_id , 'سایر مدارک'))
        except:
            return 'ندارد'
    user_document.short_description = 'مدارک کاربر '

    def all_doc(self,obj):
        display_text = "<center><a href='/api/registration/all/{}/file/zip' class = 'button' target='_blank'>مدارک</a></center>".format(obj.pk)
        return format_html(display_text)
    all_doc.short_description = format_html("<pre>            </pre>")




    def full_address(self,obj):
        return obj.user.full_address()
    full_address.short_description = 'نشانی منزل'

    def suppliers(self, obj):
        return '، '.join([supplier.name for supplier in obj.supplier_set.all() ])
    suppliers.short_description = 'تأمین کنندگان'

    def card_number(self,obj):
        display_text ='، '.join(["<center><a href='/admin/contract/vcc/{}/change' target='_blank'><b>{}</b></a></center>".format(str(contract.vcc.pk),contract.vcc_number) for contract in obj.contract_set.filter(status__in =['0','1','2','3','4']) if contract.vcc != None])
        return format_html(display_text)
    card_number.short_description = 'شماره کارت'

    def clear_contracts(self, obj):
        display_text ='، '.join(["<center><a href='/admin/contract/contract/{}/change' target='_blank'><b>{}</b></a></center>".format(str(contract.pk) , contract.contract_id) for contract in obj.contract_set.filter(status__in =['5','6']) ])
        return format_html(display_text)
    clear_contracts.short_description = 'قراردادهای تسویه شده'

    def active_contracts(self, obj):
        display_text ='، '.join(["<center><a href='/admin/contract/contract/{}/change' target='_blank'><b>{}</b></a></center>".format(str(contract.pk) , contract.contract_id) for contract in obj.contract_set.filter(status__in =['0','1','2','3','4']) ])
        return format_html(display_text)
    active_contracts.short_description = 'قراردادهای فعال'

    def suretys(self, obj):
        display_text = '، '.join(["<center><a href='/admin/customer/surety/{}/change' target='_blank'><b>{}</b></a></center>".format(str(surety.pk) , surety.__str__()) for surety in obj.suretys.all() ])
        return format_html(display_text)
    suretys.short_description = 'ضامنین'

    def far_status(self,obj):
       
        one = self.customer_status(obj)
        two = self.customer_type(obj.id)
        three = self.con_status(obj.id)
        four = self.payment_status(obj.id)
        five = self.instalment_start_date(obj.id)
        return f'{one} | {two} | {three} | {four} | {five}'
    far_status.short_description = 'وضعیت تست'

    def customer_mellicard(self,obj):
        try:
            mellicard = obj.customer_document.mellicard_front
            display_text = "<center><a href='{}' target='_blank'>{}</a></center>".format(mellicard.url , "کارت ملی")
            return format_html(display_text)
        except:
            return format_html("<center>ندارد</center>")
    customer_mellicard.short_description = 'کارت ملی'
    def customer_ice(self,obj):
        try:
            ice = obj.customer_document.credit_rate
            display_text = "<center><a href='{}' target='_blank'>{}</a></center>".format(ice.url , "رتبه اعتباری")
            return format_html(display_text)
        except:
            return format_html("<center>ندارد</center>")
    customer_ice.short_description = 'مدرک رتبه اعتباری'
    def customer_otherdoc(self,obj):
        try:
            pk = obj.customer_document.pk
            display_text = "<center><a href='/admin/document/customer_document/{}' target='_blank'>{}</a></center>".format(pk , "سایر مدارک")
            return format_html(display_text)
        except:
            return format_html("<center>ندارد</center>")
    customer_otherdoc.short_description = 'سایر مدارک'
    def suretys_ice(self,obj):
        format_text = "<center><a href='{}' target='_blank'>{}</a></center>"
        display_text = "<center>ندارد</center>"
        try:
            suretys = obj.suretys.all()
            ice = suretys[0].surety_document.credit_rate
            display_text = format_text.format(ice.url , "رتبه اعتباری ضامن اول")
            ice = suretys[1].surety_document.credit_rate
            display_text += ', ' + format_text.format(ice.url , "رتبه اعتباری ضامن دوم")
            return format_html(display_text)
        except:
            return format_html(display_text)
    suretys_ice.short_description = 'مدارک رتبه اعتباری ضامنین'

    def customer_file(self,obj):
        display_text = "<center><a href='/api/registration/{}/file/pdf' target='_blank'>فایل متقاضی</a></center>".format(obj.pk)
        return format_html(display_text)
    customer_file.short_description = 'فایل متقاضی'
    def update(modeladmin,request,queryset):
        for c in queryset:
            c.education = '3'
            c.job_class = '3'
            c.job_status = '0'
            c.home_type = '2'
            c.marital_status = '1'
            c.save()
    update.short_description = 'به روز رسانی پیش فرض ها'
    def set_to_cancel(modeladmin,request,queryset):
        for c in queryset:
            c.status = '4'
            c.save()
    set_to_cancel.short_description = 'انصراف متقاضی های انتخاب شده'
    def set_to_expired(modeladmin,request,queryset):
        for c in queryset:
            c.status = '6'
            c.save() 
            sms_text = select_MessageText().expire_credit
            send_sms(c.mobile_number, sms_text)

    set_to_expired.short_description = 'انقضای رتبه اعتباری متقاضی های انتخاب شده'
    def export_as_excel(modeladmin, request, queryset):
        workbook = xlsxwriter.Workbook(os.path.join(settings.BASE_DIR,"outputs/customer_excel.xlsx"))
        cell_format = workbook.add_format({'num_format': '#,###'})
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
        for val in CUSTOMER_EXCEL.values():
            worksheet.write(row, col , val)
            col += 1
        row += 1
        col = 0
        for c in queryset:
            col = 0
            worksheet.write(row , col , row)
            col += 1
            customer = customer_info(c)
            customer_dict = vars(customer)
            for key in CUSTOMER_EXCEL:
                data = customer_dict.get(key)
                worksheet.write(row , col , data)
                col += 1
            row += 1
        workbook.close() 
        return FileResponse(open(os.path.join(settings.BASE_DIR,"outputs/customer_excel.xlsx"),'rb'),as_attachment = True)
    export_as_excel.short_description = 'خروجی اکسل متقاضیان انتخاب شده'
admin.site.register(customer , customerAdmin)

class SuretyAdmin(admin.ModelAdmin):
    fieldsets_and_inlines_order = ()
    formfield_overrides = {
        models.IntegerField : { 'widget' : NumberInput(attrs={'size' : 40})}
    }
    list_display = ('__str__', 'melli_code' , 'mobile_number', 'job','active_contracts','clear_contracts',)
    list_filter = ()
    search_fields = ('first_name','last_name', 'melli_code', 'mobile_number')
    autocomplete_fields = ['customer']
    def clear_contracts(self, obj):
        display_text ='، '.join(["<center><a href='/admin/contract/contract/{}/change' target='_blank'><b>{}</b></a></center>".format(str(c.cont.pk) , c.cont.contract_id) for c in obj.contracts.filter(cont__status__in =['5','6']) ])
        return format_html(display_text)
    clear_contracts.short_description = 'قراردادهای تسویه شده'

    def active_contracts(self, obj):
        display_text ='، '.join(["<center><a href='/admin/contract/contract/{}/change' target='_blank'><b>{}</b></a></center>".format(str(c.cont.pk) , c.cont.contract_id) for c in obj.contracts.filter(cont__status__in =['0','1','2','21','3','4']) ])
        return format_html(display_text)
    active_contracts.short_description = 'قراردادهای فعال'
    def update(modeladmin,request,queryset):
        for c in queryset:
            c.estimate_income = c.estimate_income // 1000000
            c.save()
    update.short_description = 'به روز رسانی میزان درآمد'


class OragnAdmin(admin.ModelAdmin):
    fieldsets_and_inlines_order = ()
    list_display = ('title','id',)
admin.site.register(Organ,OragnAdmin)
class DescriptionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField : { 'widget' : Textarea(attrs={'rows': 1, 'cols': 70})}
    }
    fieldsets_and_inlines_order = ()
    exclude = ('Type',)
    list_display = ('title','id',)
admin.site.register(AcceptDescription,DescriptionAdmin)
admin.site.register(FaultDescription,DescriptionAdmin)
admin.site.register(ExpireDescription,DescriptionAdmin)
admin.site.register(CancelDescription,DescriptionAdmin)
admin.site.register(RejectDescription,DescriptionAdmin)
