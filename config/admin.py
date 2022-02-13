from django.contrib.admin.sites import AdminSite
from django.apps import apps
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _, gettext_lazy

class TestAdminSite(AdminSite):

    def get_app_list(self, request):
        app_ordering = {
            "contract": 1,
            "customer": 2,
            "supplier": 3,
            "document": 5,
            "users": 6,
            "auth": 7,
            "background_task" : 8,
            "OTP" : 9,
            "authtoken":10
        }
        customer_ordering = {
            "customer": 1,
            "surety": 2,
        }
        contract_ordering = {
            "contract" : 1,
            "payment" : 2,
            "vcc_free" : 3,
            "vcc" : 4,
            "Duration_contract": 5
        }

        app_dict = self._build_app_dict(request)
        app_list = app_dict.values()
        app_list = sorted(app_list , key = lambda x:app_ordering[x['app_label']])
        contract_order = app_ordering["contract"] - 1
        payment_order = contract_ordering["payment"]-1
        vcc_free_order = contract_ordering["vcc_free"]-1
        try:
            for app in app_list:
                if app['app_label'] == "customer":
                    temp = list()
                    for i,x in enumerate(app['models']):
                        if x['object_name'] in list(customer_ordering.keys()):
                            temp.append(app['models'][i])
                    app['models'] = temp
                    app['models'].sort(key = lambda x:customer_ordering[x['object_name']])
                elif app['app_label'] == "contract":
                    app['models'].sort(key = lambda x:contract_ordering[x['object_name']])
            if request.user.is_superuser:
                app_list[contract_order]['models'][payment_order]['add_url'] = "../contract/upload_payments"
                app_list[contract_order]['models'][vcc_free_order]['add_url'] = "../contract/upload_vccs"
        except Exception as e:
            print("except: ",str(e))
        
        return app_list
    
    def app_index(self, request, app_label, extra_context=None):
        customer_ordering = {
            "customer": 1,
            "surety": 2,
            "Organ": 3,
        }
        contract_ordering = {
            "contract" : 1,
            "payment" : 2,
            "vcc_free" : 3,
            "vcc" : 4,
            "Duration_contract": 5
        }
        vcc_free_order = contract_ordering["vcc_free"]-1
        payment_order = contract_ordering["payment"]-1
        app_dict = self._build_app_dict(request, app_label)
        if not app_dict:
            raise Http404('The requested admin page does not exist.')

        if app_label == "customer":
            temp = list()
            temp2 = list()
            for i,x in enumerate(app_dict['models']):
                if x['object_name'] in list(customer_ordering.keys()):
                    temp.append(app_dict['models'][i])
                else:
                    temp2.append(app_dict['models'][i])
            app_dict['models'] = temp
            app_dict['models'].sort(key = lambda x:customer_ordering[x['object_name']])
            app_dict['models'] += temp2

        elif app_label == "contract":
            app_dict['models'].sort(key = lambda x:contract_ordering[x['object_name']])
            try:
                if request.user.is_superuser:
                    app_dict['models'][payment_order]['add_url'] = "../../contract/upload_payments"
                    app_dict['models'][vcc_free_order]['add_url'] = "../../contract/upload_vccs"
            except:
                pass
        else:
            app_dict['models'].sort(key=lambda x: x['name'])
        app_name = apps.get_app_config(app_label).verbose_name
        context = {
            **self.each_context(request),
            'title': _('%(app)s administration') % {'app': app_name},
            'app_list': [app_dict],
            'app_label': app_label,
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, self.app_index_template or [
            'admin/%s/app_index.html' % app_label,
            'admin/app_index.html'
        ], context)
