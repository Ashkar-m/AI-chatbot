from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('details/', views.details, name='details'),
    path('payment/', views.payment, name='payment'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('email_exists/', views.email_exists, name='email_exists'),
    path('create-paymet-intent/', views.create_payment_intent, name='create_name_intent'),
]