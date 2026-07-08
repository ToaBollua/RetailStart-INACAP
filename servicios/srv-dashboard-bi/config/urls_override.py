from django.urls import path, include
from django.contrib import admin
from analytics import views as analytics_views

urlpatterns = [
    path('', analytics_views.dashboard, name='home'),
    path('admin/', admin.site.urls),
    path('analytics/dashboard/', analytics_views.dashboard, name='dashboard'),
    path('analytics/api/kpi-data/', analytics_views.kpi_data_json, name='kpi_data'),
    path('analytics/export/csv/', analytics_views.export_csv, name='export_csv'),
    path('analytics/export/json/', analytics_views.export_json, name='export_json'),
    path('analytics/export/pdf/', analytics_views.export_pdf, name='export_pdf'),
]
