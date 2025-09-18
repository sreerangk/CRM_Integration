from typing import List
import random
import time
import logging

from file_synch.services.crm_providers import BaseCRMService, CRMDeal, CRMFile

logger = logging.getLogger(__name__)

class ZohoService(BaseCRMService):
    """Mock Zoho CRM service for testing"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://www.zohoapis.com/crm/v2")
        self.name = "Zoho"
    
    def authenticate(self) -> bool:
        """Mock authentication"""
        logger.info(f"Authenticating with {self.name}")
        time.sleep(0.1)
        return True
    
    def get_deals(self) -> List[CRMDeal]:
        """Mock deals data"""
        logger.info(f"Fetching deals from {self.name}")
        mock_deals = [
            CRMDeal("zh_deal_001", "TechCorp Partnership", 80000, "presentation"),
            CRMDeal("zh_deal_002", "StartUp Seed Deal", 15000, "prospecting"),
            CRMDeal("zh_deal_003", "Enterprise Solution", 120000, "closed-won"),
            CRMDeal("zh_deal_004", "SMB Package", 8000, "proposal"),
            CRMDeal("zh_deal_005", "Consulting Services", 45000, "negotiation"),
        ]
        return mock_deals
    
    def get_files_for_deal(self, deal_id: str) -> List[CRMFile]:
        """Mock files data for deals"""
        logger.info(f"Fetching files for deal {deal_id} from {self.name}")
        
        file_templates = [
            ("agreement.pdf", "pdf", 1024*800),    # 800KB
            ("specifications.doc", "doc", 1024*250),  # 250KB
            ("financial_report.xlsx", "xlsx", 1024*400),  # 400KB
            ("presentation.pptx", "other", 1024*600),  # 600KB
            ("screenshot.jpg", "jpg", 1024*100),    # 100KB
            ("notes.txt", "txt", 1024*5),          # 5KB
        ]
        
        files = []
        num_files = random.randint(1, 5)
        selected_templates = random.sample(file_templates, min(num_files, len(file_templates)))
        
        for i, (name, ext, size) in enumerate(selected_templates):
            file_id = f"zh_file_{deal_id}_{i+1:03d}"
            file_name = f"{deal_id}_{name}"
            file_url = f"https://www.zohoapis.com/crm/v2/files/{file_id}/content"
            
            files.append(CRMFile(
                file_id=file_id,
                name=file_name,
                size=size + random.randint(-2000, 2000),
                file_type=ext,
                url=file_url,
                deal_id=deal_id
            ))
        
        return files
    
    def download_file(self, file_url: str) -> bytes:
        """Mock file download"""
        logger.info(f"Downloading file from {file_url}")
        time.sleep(0.3)  # Simulate download time
        return b"Mock file content for Zoho file"