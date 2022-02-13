"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views
from users.views import TokenObtainPair_supp,TokenObtainPair_cust

admin.site.site_header = "مدیریت تست"
admin.site.site_title = "مدیریت تست"

urlpatterns = [
	path('admin/', admin.site.urls),
	path('api/supplier/', include('supplier.urls')),
	path('login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('login/supplier/', TokenObtainPair_supp.as_view(), name='token_obtain_pair_supp'),
	path('login/customer/', TokenObtainPair_cust.as_view(), name='token_obtain_pair_cust'),
	path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
	path("token/verify/", jwt_views.TokenVerifyView.as_view(), name="jwt-verify"),
	path('', include('djoser.urls')),
	path("api/registration/", include("OTP.urls")),
	path("api/registration/", include("customer.urls")),
	path("api/document/", include("document.urls")),
	path('contract/', include('contract.urls')),
	path('api/admin/', include('users.urls')),
]

if settings.DEBUG == True:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)