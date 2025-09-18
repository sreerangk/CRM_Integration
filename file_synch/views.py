
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator

from CRM_Integration import settings
from file_synch.services.crm_factory import CRMServiceFactory
from file_synch.services.sync_service import FileSyncService
from file_synch.tasks import sync_files_task
from .models import CRMProvider, Deal, FileMetadata, SyncLog

import json
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class CRMProvidersView(View):
    """API endpoint for CRM providers"""
    
    def get(self, request):
        """List all CRM providers"""
        providers = CRMProvider.objects.all()
        data = [{
            'id': p.id,
            'name': p.name,
            'api_endpoint': p.api_endpoint,
            'is_active': p.is_active,
            'deals_count': p.deal_set.count(),
        } for p in providers]
        
        return JsonResponse({'providers': data})

@method_decorator(csrf_exempt, name='dispatch')
class DealsView(View):
    """API endpoint for deals"""
    
    def get(self, request):
        """List deals with optional filtering"""
        crm_provider_id = request.GET.get('crm_provider')
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        queryset = Deal.objects.select_related('crm_provider').all()
        
        if crm_provider_id:
            queryset = queryset.filter(crm_provider_id=crm_provider_id)
        
        if search:
            queryset = queryset.filter(
                Q(deal_name__icontains=search) |
                Q(crm_deal_id__icontains=search)
            )
        
        queryset = queryset.annotate(files_count=Count('files'))
        queryset = queryset.order_by('-created_at')
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = [{
            'id': deal.id,
            'crm_provider': deal.crm_provider.name,
            'crm_deal_id': deal.crm_deal_id,
            'deal_name': deal.deal_name,
            'deal_amount': float(deal.deal_amount) if deal.deal_amount else None,
            'deal_stage': deal.deal_stage,
            'files_count': deal.files_count,
            'created_at': deal.created_at.isoformat(),
        } for deal in page_obj]
        
        return JsonResponse({
            'deals': data,
            'pagination': {
                'total': paginator.count,
                'pages': paginator.num_pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })

@method_decorator(csrf_exempt, name='dispatch')
class FilesView(View):

    def get(self, request):
        deal_id = request.GET.get('deal_id')
        crm_provider_id = request.GET.get('crm_provider')
        file_type = request.GET.get('file_type')
        sync_status = request.GET.get('sync_status')
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        queryset = FileMetadata.objects.select_related('deal__crm_provider').all()
        
        # Apply filters
        if deal_id:
            queryset = queryset.filter(deal_id=deal_id)
        
        if crm_provider_id:
            queryset = queryset.filter(deal__crm_provider_id=crm_provider_id)
        
        if file_type:
            queryset = queryset.filter(file_type=file_type)
        
        if sync_status:
            queryset = queryset.filter(sync_status=sync_status)
        
        if search:
            queryset = queryset.filter(file_name__icontains=search)
        
        # Ordering
        order_by = request.GET.get('order_by', '-created_at')
        queryset = queryset.order_by(order_by)
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = [{
            'id': str(file.id),
            'deal_id': file.deal.id,
            'deal_name': file.deal.deal_name,
            'crm_provider': file.deal.crm_provider.name,
            'crm_file_id': file.crm_file_id,
            'file_name': file.file_name,
            'file_size': file.file_size,
            'file_size_mb': round(file.file_size / (1024 * 1024), 2),
            'file_type': file.file_type,
            'sync_status': file.sync_status,
            'sync_timestamp': file.sync_timestamp.isoformat() if file.sync_timestamp else None,
            'created_at': file.created_at.isoformat(),
        } for file in page_obj]
        
        return JsonResponse({
            'files': data,
            'pagination': {
                'total': paginator.count,
                'pages': paginator.num_pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })

@method_decorator(csrf_exempt, name='dispatch')
class SyncView(View):
    """API endpoint for file synchronization"""
    
    def post(self, request):
        """Trigger file synchronization"""
        try:
            data = json.loads(request.body)
            crm_provider_id = data.get('crm_provider_id')
            file_ids = data.get('file_ids', [])  # Optional: specific files to sync
            
            if not crm_provider_id:
                return JsonResponse({'error': 'crm_provider_id is required'}, status=400)
            
            # try:
            #     crm_provider = CRMProvider.objects.get(id=crm_provider_id, is_active=True)
            # except CRMProvider.DoesNotExist:
            #     return JsonResponse({'error': 'CRM provider not found or inactive'}, status=404)
            
            # sync_service = FileSyncService(crm_provider)
            
            # if file_ids:
            #     # Sync specific files
            #     results = sync_service.sync_specific_files(file_ids)
            #     message = f"Selective sync completed for {len(file_ids)} file(s)"
            # else:
            #     # Full sync
            #     results = sync_service.sync_all_files()
            #     message = "Full sync completed"
            # return JsonResponse({
            #     'message': message,
            #     'results': results
            # })
            # Trigger Celery task
            task = sync_files_task.delay(crm_provider_id, file_ids)
            return JsonResponse({
                'message': 'Sync task has been queued',
                'task_id': task.id
            })
           
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            logger.error(f"Sync failed: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class AvailableFilesView(View):
    """API endpoint to list available files from CRM without syncing"""
    
    def get(self, request):
        """List all available files from CRM"""
        crm_provider_id = request.GET.get('crm_provider_id')
        
        if not crm_provider_id:
            return JsonResponse({'error': 'crm_provider_id is required'}, status=400)
        
        try:
            crm_provider = CRMProvider.objects.get(id=crm_provider_id, is_active=True)
        except CRMProvider.DoesNotExist:
            return JsonResponse({'error': 'CRM provider not found or inactive'}, status=404)
        
        try:
            api_key = settings.CRM_API_KEY 
            crm_service = CRMServiceFactory.create_service(
                crm_provider.name.lower(),
                api_key
            )
            
            if not crm_service:
                return JsonResponse({'error': 'Unsupported CRM provider'}, status=400)
            
            # Authenticate
            if not crm_service.authenticate():
                return JsonResponse({'error': 'CRM authentication failed'}, status=401)
            
            # Get all deals and their files
            crm_deals = crm_service.get_deals()
            all_files = []
            
            for deal in crm_deals:
                crm_files = crm_service.get_files_for_deal(deal.deal_id)
                for crm_file in crm_files:
                    # Check if file is already synced
                    try:
                        db_deal = Deal.objects.get(
                            crm_provider=crm_provider,
                            crm_deal_id=deal.deal_id
                        )
                        is_synced = FileMetadata.objects.filter(
                            deal=db_deal,
                            crm_file_id=crm_file.file_id
                        ).exists()
                    except Deal.DoesNotExist:
                        is_synced = False
                    
                    all_files.append({
                        'crm_file_id': crm_file.file_id,
                        'file_name': crm_file.name,
                        'file_size': crm_file.size,
                        'file_size_mb': round(crm_file.size / (1024 * 1024), 2),
                        'file_type': crm_file.file_type,
                        'deal_id': deal.deal_id,
                        'deal_name': deal.name,
                        'is_synced': is_synced
                    })
            
            return JsonResponse({
                'crm_provider': crm_provider.name,
                'files': all_files,
                'total_files': len(all_files)
            })
            
        except Exception as e:
            logger.error(f"Error fetching available files: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class SyncLogsView(View):
    """API endpoint for sync logs"""
    
    def get(self, request):
        """List sync logs"""
        crm_provider_id = request.GET.get('crm_provider')
        level = request.GET.get('level')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 50))
        
        queryset = SyncLog.objects.select_related('crm_provider').all()
        
        if crm_provider_id:
            queryset = queryset.filter(crm_provider_id=crm_provider_id)
        
        if level:
            queryset = queryset.filter(level=level)
        
        queryset = queryset.order_by('-created_at')
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = [{
            'id': log.id,
            'crm_provider': log.crm_provider.name,
            'level': log.level,
            'message': log.message,
            'file_id': str(log.file_metadata.id) if log.file_metadata else None,
            'created_at': log.created_at.isoformat(),
        } for log in page_obj]
        
        return JsonResponse({
            'logs': data,
            'pagination': {
                'total': paginator.count,
                'pages': paginator.num_pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })

class StatsView(View):
    """API endpoint for statistics"""
    
    def get(self, request):
        """Get sync statistics"""
        crm_provider_id = request.GET.get('crm_provider')
        
        base_files = FileMetadata.objects.select_related('deal__crm_provider')
        
        if crm_provider_id:
            base_files = base_files.filter(deal__crm_provider_id=crm_provider_id)
        
        stats = {
            'total_files': base_files.count(),
            'synced_files': base_files.filter(sync_status='synced').count(),
            'failed_files': base_files.filter(sync_status='failed').count(),
            'pending_files': base_files.filter(sync_status='pending').count(),
            'total_size_bytes': sum(base_files.values_list('file_size', flat=True)),
            'files_by_type': {},
            'files_by_crm': {},
        }
        
        # Calculate total size in MB
        stats['total_size_mb'] = round(stats['total_size_bytes'] / (1024 * 1024), 2)
        
        # Files by type
        for choice in FileMetadata.FILE_TYPES:
            file_type = choice[0]
            count = base_files.filter(file_type=file_type).count()
            if count > 0:
                stats['files_by_type'][file_type] = count
        
        # Files by CRM provider
        crm_stats = base_files.values('deal__crm_provider__name').annotate(
            count=Count('id')
        )
        for stat in crm_stats:
            stats['files_by_crm'][stat['deal__crm_provider__name']] = stat['count']
        
        return JsonResponse(stats)
