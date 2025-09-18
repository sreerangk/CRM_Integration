from django.db import models
from django.utils import timezone
import uuid

class CRMProvider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    api_endpoint = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'crm_providers'

class Deal(models.Model):
    crm_provider = models.ForeignKey(CRMProvider, on_delete=models.CASCADE)
    crm_deal_id = models.CharField(max_length=100)
    deal_name = models.CharField(max_length=255)
    deal_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    deal_stage = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['crm_provider', 'crm_deal_id']
        indexes = [
            models.Index(fields=['crm_provider', 'crm_deal_id']),
            models.Index(fields=['deal_name']),
        ]
        db_table = 'deals'
    
    def __str__(self):
        return f"{self.deal_name} ({self.crm_provider.name})"

class FileMetadata(models.Model):
    FILE_TYPES = [
        ('pdf', 'PDF'),
        ('doc', 'Document'),
        ('docx', 'Word Document'),
        ('xls', 'Excel'),
        ('xlsx', 'Excel Document'),
        ('jpg', 'JPEG Image'),
        ('png', 'PNG Image'),
        ('txt', 'Text File'),
        ('other', 'Other'),
    ]
    
    SYNC_STATUS = [
        ('pending', 'Pending'),
        ('synced', 'Synced'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='files')
    crm_file_id = models.CharField(max_length=100)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # Size in bytes
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    file_url = models.URLField()
    sync_status = models.CharField(max_length=10, choices=SYNC_STATUS, default='pending')
    sync_timestamp = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['deal', 'crm_file_id']
        indexes = [
            models.Index(fields=['file_type']),
            models.Index(fields=['sync_status']),
            models.Index(fields=['sync_timestamp']),
            models.Index(fields=['deal', 'crm_file_id']),
            models.Index(fields=['file_name']),
        ]
        db_table = 'file_metadata'
    
    def __str__(self):
        return f"{self.file_name} - {self.deal.deal_name}"

class SyncLog(models.Model):
    LOG_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    crm_provider = models.ForeignKey(CRMProvider, on_delete=models.CASCADE)
    level = models.CharField(max_length=10, choices=LOG_LEVELS)
    message = models.TextField()
    file_metadata = models.ForeignKey(FileMetadata, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['crm_provider', 'created_at']),
            models.Index(fields=['level']),
        ]
        db_table = 'sync_logs'