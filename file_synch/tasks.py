from celery import shared_task
from file_synch.services.sync_service import FileSyncService
from .models import CRMProvider
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def sync_files_task(self, crm_provider_id, file_ids=None):
    try:
        crm_provider = CRMProvider.objects.get(id=crm_provider_id, is_active=True)
        service = FileSyncService(crm_provider)

        if file_ids:
            results = service.sync_specific_files(file_ids)
            message = f"Selective sync completed for {len(file_ids)} file(s)"
        else:
            results = service.sync_all_files()
            message = "Full sync completed"

        return {
            'status': 'success',
            'message': message,
            'results': results
        }

    except CRMProvider.DoesNotExist:
        logger.error(f"CRM provider {crm_provider_id} not found or inactive")
        return {'status': 'error', 'message': 'CRM provider not found or inactive'}

    except Exception as e:
        logger.error(f"Sync failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}