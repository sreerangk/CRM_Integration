from CRM_Integration import settings
from django.db import transaction
from django.utils import timezone

from file_synch.models import CRMProvider, Deal, FileMetadata, SyncLog
from .crm_factory import CRMServiceFactory
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FileSyncService:
    """Service for synchronizing files from CRM to database"""
    
    def __init__(self, crm_provider: CRMProvider):
        self.crm_provider = crm_provider
        
        api_key = settings.CRM_API_KEY 
        self.crm_service = CRMServiceFactory.create_service(
            crm_provider.name.lower(),
            api_key  # Mock API key for demo
        )
        
        if not self.crm_service:
            raise ValueError(f"Unsupported CRM provider: {crm_provider.name}")
    
    def sync_all_files(self) -> Dict[str, Any]:
        """Sync all files from CRM"""
        logger.info(f"Starting full sync for {self.crm_provider.name}")
        
        try:
            # Authenticate with CRM
            if not self.crm_service.authenticate():
                raise Exception("CRM authentication failed")
            
            # Get all deals
            crm_deals = self.crm_service.get_deals()
            
            results = {
                'deals_processed': 0,
                'files_synced': 0,
                'files_updated': 0,
                'files_failed': 0,
                'errors': []
            }
            
            for crm_deal in crm_deals:
                try:
                    # Create or update deal
                    deal, created = Deal.objects.get_or_create(
                        crm_provider=self.crm_provider,
                        crm_deal_id=crm_deal.deal_id,
                        defaults={
                            'deal_name': crm_deal.name,
                            'deal_amount': crm_deal.amount,
                            'deal_stage': crm_deal.stage,
                        }
                    )
                    
                    if not created:
                        # Update existing deal
                        deal.deal_name = crm_deal.name
                        deal.deal_amount = crm_deal.amount
                        deal.deal_stage = crm_deal.stage
                        deal.save()
                    
                    results['deals_processed'] += 1
                    
                    # Get files for this deal
                    crm_files = self.crm_service.get_files_for_deal(crm_deal.deal_id)
                    
                    for crm_file in crm_files:
                        file_result = self._sync_file(deal, crm_file)
                        results[f"files_{file_result}"] += 1
                        
                except Exception as e:
                    error_msg = f"Error processing deal {crm_deal.deal_id}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
                    self._log_sync_error(error_msg)
            
            self._log_sync_info(f"Sync completed. Results: {results}")
            return results
            
        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            logger.error(error_msg)
            self._log_sync_error(error_msg)
            raise
    
    def sync_specific_files(self, file_ids: List[str]) -> Dict[str, Any]:
        """Sync specific files by their CRM file IDs"""
        logger.info(f"Starting selective sync for files: {file_ids}")
        
        results = {
            'files_synced': 0,
            'files_updated': 0,
            'files_failed': 0,
            'errors': []
        }
        
        try:
            if not self.crm_service.authenticate():
                raise Exception("CRM authentication failed")
            
            # Get all deals first
            crm_deals = self.crm_service.get_deals()
            
            for crm_deal in crm_deals:
                crm_files = self.crm_service.get_files_for_deal(crm_deal.deal_id)
                
                for crm_file in crm_files:
                    if crm_file.file_id in file_ids:
                        try:
                            # Ensure deal exists
                            deal, _ = Deal.objects.get_or_create(
                                crm_provider=self.crm_provider,
                                crm_deal_id=crm_deal.deal_id,
                                defaults={
                                    'deal_name': crm_deal.name,
                                    'deal_amount': crm_deal.amount,
                                    'deal_stage': crm_deal.stage,
                                }
                            )
                            
                            file_result = self._sync_file(deal, crm_file)
                            results[f"files_{file_result}"] += 1
                            
                        except Exception as e:
                            error_msg = f"Error syncing file {crm_file.file_id}: {str(e)}"
                            logger.error(error_msg)
                            results['errors'].append(error_msg)
                            results['files_failed'] += 1
            
            return results
            
        except Exception as e:
            error_msg = f"Selective sync failed: {str(e)}"
            logger.error(error_msg)
            self._log_sync_error(error_msg)
            raise
    
    @transaction.atomic
    def _sync_file(self, deal: Deal, crm_file) -> str:
        """Sync individual file"""
        try:
            # Check if file already exists
            file_metadata, created = FileMetadata.objects.get_or_create(
                deal=deal,
                crm_file_id=crm_file.file_id,
                defaults={
                    'file_name': crm_file.name,
                    'file_size': crm_file.size,
                    'file_type': crm_file.file_type,
                    'file_url': crm_file.url,
                    'sync_status': 'synced',
                    'sync_timestamp': timezone.now(),
                }
            )
            
            if not created:
                # Update existing file if changed
                updated = False
                if file_metadata.file_name != crm_file.name:
                    file_metadata.file_name = crm_file.name
                    updated = True
                if file_metadata.file_size != crm_file.size:
                    file_metadata.file_size = crm_file.size
                    updated = True
                if file_metadata.file_url != crm_file.url:
                    file_metadata.file_url = crm_file.url
                    updated = True
                
                if updated:
                    file_metadata.sync_status = 'synced'
                    file_metadata.sync_timestamp = timezone.now()
                    file_metadata.save()
                    return 'updated'
                
                return 'synced'  # No changes needed
            
            return 'synced'
            
        except Exception as e:
            # Mark file as failed
            file_metadata, _ = FileMetadata.objects.get_or_create(
                deal=deal,
                crm_file_id=crm_file.file_id,
                defaults={
                    'file_name': crm_file.name,
                    'file_size': crm_file.size,
                    'file_type': crm_file.file_type,
                    'file_url': crm_file.url,
                    'sync_status': 'failed',
                }
            )
            file_metadata.sync_status = 'failed'
            file_metadata.save()
            
            error_msg = f"Failed to sync file {crm_file.file_id}: {str(e)}"
            self._log_sync_error(error_msg, file_metadata)
            raise Exception(error_msg)
    
    def _log_sync_info(self, message: str):
        """Log sync information"""
        SyncLog.objects.create(
            crm_provider=self.crm_provider,
            level='info',
            message=message
        )
    
    def _log_sync_error(self, message: str, file_metadata=None):
        """Log sync error"""
        SyncLog.objects.create(
            crm_provider=self.crm_provider,
            level='error',
            message=message,
            file_metadata=file_metadata
        )