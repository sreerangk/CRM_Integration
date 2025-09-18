
from file_synch.models import CRMProvider
from file_synch.services.sync_service import FileSyncService
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Sync files from CRM systems'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--provider',
            type=str,
            help='CRM provider name (hubspot, zoho)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync from all active providers',
        )
        parser.add_argument(
            '--files',
            nargs='+',
            help='Specific file IDs to sync',
        )
    
    def handle(self, *args, **options):
        if options['all']:
            providers = CRMProvider.objects.filter(is_active=True)
        elif options['provider']:
            try:
                providers = [CRMProvider.objects.get(name__iexact=options['provider'], is_active=True)]
            except CRMProvider.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Provider "{options["provider"]}" not found or inactive')
                )
                return
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --provider or --all')
            )
            return
        
        for provider in providers:
            self.stdout.write(f'Syncing files from {provider.name}...')
            
            try:
                sync_service = FileSyncService(provider)
                
                if options['files']:
                    results = sync_service.sync_specific_files(options['files'])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Selective sync completed for {provider.name}: '
                            f'{results["files_synced"]} synced, '
                            f'{results["files_updated"]} updated, '
                            f'{results["files_failed"]} failed'
                        )
                    )
                else:
                    # Full sync
                    results = sync_service.sync_all_files()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Full sync completed for {provider.name}: '
                            f'{results["deals_processed"]} deals, '
                            f'{results["files_synced"]} files synced, '
                            f'{results["files_updated"]} files updated, '
                            f'{results["files_failed"]} files failed'
                        )
                    )
                
                if results['errors']:
                    for error in results['errors']:
                        self.stdout.write(self.style.WARNING(f'Warning: {error}'))
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Sync failed for {provider.name}: {str(e)}')
                )
