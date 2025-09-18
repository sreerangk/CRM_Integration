from .crm_providers import BaseCRMService
from .hubspot_service import HubSpotService
from .zoho_service import ZohoService
from typing import Optional

class CRMServiceFactory:
    """Factory class for creating CRM service instances"""
    
    _services = {
        'hubspot': HubSpotService,
        'zoho': ZohoService,
    }
    
    @classmethod
    def create_service(cls, provider_name: str, api_key: str) -> Optional[BaseCRMService]:
        """Create CRM service instance based on provider name"""
        service_class = cls._services.get(provider_name.lower())
        if service_class:
            return service_class(api_key)
        return None
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """Get list of supported CRM providers"""
        return list(cls._services.keys())