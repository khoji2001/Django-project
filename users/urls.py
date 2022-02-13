from django.urls import path 
from .views import *

app_name = 'users'

urlpatterns = [
        path('calculator', calculator ,name='calculator'),
        # path('calculato', calculato ,name='calculato'),
        path('download' , download_excell , name = 'download'),
]