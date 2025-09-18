
from file_synch.models import CRMProvider
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Setup initial CRM providers'
    
    def handle(self, *args, **options):
        providers = [
            {
                'name': 'HubSpot',
                'api_endpoint': 'https://api.hubapi.com',
            },
            {
                'name': 'Zoho',
                'api_endpoint': 'https://www.zohoapis.com/crm/v2',
            }
        ]
        
        for provider_data in providers:
            provider, created = CRMProvider.objects.get_or_create(
                name=provider_data['name'],
                defaults=provider_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created CRM provider: {provider.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'CRM provider already exists: {provider.name}')
                )