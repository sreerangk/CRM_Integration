from django.contrib import admin
from .models import CRMProvider, Deal, FileMetadata, SyncLog

# Register all models with default admin
admin.site.register(CRMProvider)
admin.site.register(Deal)
admin.site.register(FileMetadata)
admin.site.register(SyncLog)