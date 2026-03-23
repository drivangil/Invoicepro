from django.urls import path
from . import views

app_name = 'scanner'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('upload/', views.upload_invoices_view, name='upload'),
    path('save/', views.save_confirmed_invoices_view, name='save'),
    path('config/', views.config_view, name='config'),
    path('export-excel/', views.export_excel_view, name='export_excel'),
    path('delete/<int:pk>/', views.delete_invoice_view, name='delete'),
]
