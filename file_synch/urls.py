from django.urls import path
from . import views

urlpatterns = [
    path('api/crm-providers/', views.CRMProvidersView.as_view(), name='crm-providers'),
    path('api/deals/', views.DealsView.as_view(), name='deals'),
    path('api/files/', views.FilesView.as_view(), name='files'),
    path('api/available-files/', views.AvailableFilesView.as_view(), name='available-files'),
    path('api/sync/', views.SyncView.as_view(), name='sync'),
    path('api/sync-logs/', views.SyncLogsView.as_view(), name='sync-logs'),
    path('api/stats/', views.StatsView.as_view(), name='stats'),
]