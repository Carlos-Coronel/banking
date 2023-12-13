from django.urls import path
from .views import record_auditoria_api
app_name = 'api_auditoria'

urlpatterns = [
    path('record/<str:evento>/<str:nivel>/', record_auditoria_api, name='record_auditoria_api'),
]
