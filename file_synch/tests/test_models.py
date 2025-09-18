from django.test import TestCase
from django.core.exceptions import ValidationError

from file_synch.models import CRMProvider, Deal, FileMetadata

class CRMProviderTest(TestCase):
    def test_create_crm_provider(self):
        provider = CRMProvider.objects.create(
            name='Test CRM',
            api_endpoint='https://api.test.com'
        )
        self.assertEqual(provider.name, 'Test CRM')
        self.assertTrue(provider.is_active)
    
    def test_unique_provider_name(self):
        CRMProvider.objects.create(
            name='Test CRM',
            api_endpoint='https://api.test.com'
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            CRMProvider.objects.create(
                name='Test CRM',
                api_endpoint='https://api2.test.com'
            )

class DealTest(TestCase):
    def setUp(self):
        self.provider = CRMProvider.objects.create(
            name='Test CRM',
            api_endpoint='https://api.test.com'
        )
    
    def test_create_deal(self):
        deal = Deal.objects.create(
            crm_provider=self.provider,
            crm_deal_id='test_deal_001',
            deal_name='Test Deal',
            deal_amount=10000.00
        )
        self.assertEqual(deal.deal_name, 'Test Deal')
        self.assertEqual(deal.deal_amount, 10000.00)
    
    def test_unique_deal_per_provider(self):
        Deal.objects.create(
            crm_provider=self.provider,
            crm_deal_id='test_deal_001',
            deal_name='Test Deal'
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            Deal.objects.create(
                crm_provider=self.provider,
                crm_deal_id='test_deal_001',
                deal_name='Another Deal'
            )

class FileMetadataTest(TestCase):
    def setUp(self):
        self.provider = CRMProvider.objects.create(
            name='Test CRM',
            api_endpoint='https://api.test.com'
        )
        self.deal = Deal.objects.create(
            crm_provider=self.provider,
            crm_deal_id='test_deal_001',
            deal_name='Test Deal'
        )
    
    def test_create_file_metadata(self):
        file_meta = FileMetadata.objects.create(
            deal=self.deal,
            crm_file_id='test_file_001',
            file_name='test.pdf',
            file_size=1024000,
            file_type='pdf',
            file_url='https://api.test.com/files/test_file_001'
        )
        self.assertEqual(file_meta.file_name, 'test.pdf')
        self.assertEqual(file_meta.sync_status, 'pending')
    
    def test_unique_file_per_deal(self):
        FileMetadata.objects.create(
            deal=self.deal,
            crm_file_id='test_file_001',
            file_name='test.pdf',
            file_size=1024000,
            file_type='pdf',
            file_url='https://api.test.com/files/test_file_001'
        )
        
        with self.assertRaises(Exception):  # IntegrityError
            FileMetadata.objects.create(
                deal=self.deal,
                crm_file_id='test_file_001',
                file_name='another.pdf',
                file_size=2048000,
                file_type='pdf',
                file_url='https://api.test.com/files/test_file_001'
            )