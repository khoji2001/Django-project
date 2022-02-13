
from django.contrib.admin.apps import AdminConfig

class TestAdminConfig(AdminConfig):
    default_site = 'config.admin.TestAdminSite'