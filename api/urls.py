# api_app/urls.py
from django.urls import path
from .views import transaction_list, api_list, user_bank_account

app_name = 'api_app'  # Agrega un espacio de nombres

urlpatterns = [
    path('celestial/report/', transaction_list, name='transaction-report'),
    path('api-list/', api_list, name='api-list'),
    path('user/balance/', user_bank_account, name='user-balance'),
    path('celestial/report/<str:daterange>/', transaction_list, name='transaction-report-filtered'),
]
