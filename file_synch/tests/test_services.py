import unittest
from django.test import TestCase
from unittest.mock import Mock, patch

from file_synch.services.crm_factory import CRMServiceFactory
from file_synch.services.hubspot_service import HubSpotService
from file_synch.models import CRMProvider
from file_synch.services.sync_service import FileSyncService
from file_synch.services.zoho_service import ZohoService

class CRMServiceFactoryTest(TestCase):
    def test_create_hubspot_service(self):
        service = CRMServiceFactory.create_service('hubspot', 'test_key')
        self.assertIsInstance(service, HubSpotService)
    
    def test_create_zoho_service(self):
        service = CRMServiceFactory.create_service('zoho', 'test_key')
        self.assertIsInstance(service, ZohoService)
    
    def test_create_invalid_service(self):
        service = CRMServiceFactory.create_service('invalid', 'test_key')
        self.assertIsNone(service)
    
    def test_get_supported_providers(self):
        providers = CRMServiceFactory.get_supported_providers()
        self.assertIn('hubspot', providers)
        self.assertIn('zoho', providers)

class HubSpotServiceTest(TestCase):
    def setUp(self):
        self.service = HubSpotService('test_api_key')
    
    def test_authenticate(self):
        result = self.service.authenticate()
        self.assertTrue(result)
    
    def test_get_deals(self):
        deals = self.service.get_deals()
        self.assertGreater(len(deals), 0)
        self.assertEqual(deals[0].deal_id, 'hs_deal_001')
    
    def test_get_files_for_deal(self):
        files = self.service.get_files_for_deal('hs_deal_001')
        self.assertGreater(len(files), 0)
        self.assertTrue(files[0].file_id.startswith('hs_file_'))
    
    def test_download_file(self):
        content = self.service.download_file('https://test.com/file')
        self.assertIsInstance(content, bytes)

class ZohoServiceTest(TestCase):
    def setUp(self):
        self.service = ZohoService('test_api_key')
    
    def test_authenticate(self):
        result = self.service.authenticate()
        self.assertTrue(result)
    
    def test_get_deals(self):
        deals = self.service.get_deals()
        self.assertGreater(len(deals), 0)
        self.assertEqual(deals[0].deal_id, 'zh_deal_001')
    
    def test_get_files_for_deal(self):
        files = self.service.get_files_for_deal('zh_deal_001')
        self.assertGreater(len(files), 0)
        self.assertTrue(files[0].file_id.startswith('zh_file_'))

class SyncServiceTest(TestCase):
    def setUp(self):
        self.crm_provider = CRMProvider.objects.create(
            name='HubSpot',
            api_endpoint='https://api.hubapi.com'
        )
        self.sync_service = FileSyncService(self.crm_provider)
    
    def test_sync_service_creation(self):
        self.assertEqual(self.sync_service.crm_provider, self.crm_provider)
        self.assertIsNotNone(self.sync_service.crm_service)
    
    def test_invalid_crm_provider(self):
        invalid_provider = CRMProvider.objects.create(
            name='InvalidCRM',
            api_endpoint='https://invalid.com'
        )
        
        with self.assertRaises(ValueError):
            FileSyncService(invalid_provider)