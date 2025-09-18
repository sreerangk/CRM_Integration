from django.test import TestCase, Client
from django.urls import reverse
import json

from file_synch.models import CRMProvider, Deal, FileMetadata

class APIViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.provider = CRMProvider.objects.create(
            name='HubSpot',
            api_endpoint='https://api.hubapi.com'
        )
        self.deal = Deal.objects.create(
            crm_provider=self.provider,
            crm_deal_id='test_deal_001',
            deal_name='Test Deal'
        )
    
    def test_crm_providers_endpoint(self):
        response = self.client.get('/api/crm-providers/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('providers', data)
        self.assertEqual(len(data['providers']), 1)
    
    def test_deals_endpoint(self):
        response = self.client.get('/api/deals/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('deals', data)
        self.assertIn('pagination', data)
    
    def test_files_endpoint(self):
        # Create a file first
        FileMetadata.objects.create(
            deal=self.deal,
            crm_file_id='test_file_001',
            file_name='test.pdf',
            file_size=1024000,
            file_type='pdf',
            file_url='https://api.test.com/files/test_file_001'
        )
        
        response = self.client.get('/api/files/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('files', data)
        self.assertEqual(len(data['files']), 1)
    
    # def test_sync_endpoint(self):
    #     response = self.client.post(
    #         '/api/sync/',
    #         json.dumps({'crm_provider_id': self.provider.id}),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.content)
    #     self.assertIn('results', data)
    # for celery 
    def test_sync_endpoint(self):
        response = self.client.post(
            '/api/sync/',
            json.dumps({'crm_provider_id': self.provider.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        # Check for async task response instead of 'results'
        self.assertIn('task_id', data)
        self.assertEqual(data['message'], 'Sync task has been queued')
    def test_available_files_endpoint(self):
        response = self.client.get(f'/api/available-files/?crm_provider_id={self.provider.id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('files', data)
        self.assertIn('total_files', data)
    
    def test_stats_endpoint(self):
        response = self.client.get('/api/stats/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('total_files', data)
        self.assertIn('files_by_type', data)