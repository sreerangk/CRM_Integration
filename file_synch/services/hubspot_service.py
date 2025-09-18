from typing import List
import random
import time
import logging

from file_synch.services.crm_providers import BaseCRMService, CRMDeal, CRMFile

logger = logging.getLogger(__name__)

class HubSpotService(BaseCRMService):
    """Mock HubSpot CRM service for testing"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.hubapi.com")
        self.name = "HubSpot"
    
    def authenticate(self) -> bool:
        """Mock authentication - always returns True for demo"""
        logger.info(f"Authenticating with {self.name}")
        # Simulate API call delay
        time.sleep(0.1)
        return True
    
    def get_deals(self) -> List[CRMDeal]:
        """Mock deals data"""
        logger.info(f"Fetching deals from {self.name}")
        mock_deals = [
            CRMDeal("hs_deal_001", "Acme Corp Contract", 50000, "negotiation"),
            CRMDeal("hs_deal_002", "Beta Industries License", 25000, "proposal"),
            CRMDeal("hs_deal_003", "Gamma Solutions Agreement", 75000, "closed-won"),
            CRMDeal("hs_deal_004", "Delta Partners Deal", 30000, "qualification"),
        ]
        return mock_deals
    
    def get_files_for_deal(self, deal_id: str) -> List[CRMFile]:
        """Mock files data for deals"""
        logger.info(f"Fetching files for deal {deal_id} from {self.name}")
        
        file_templates = [
            ("contract_v1.pdf", "pdf", 1024*500),  # 500KB
            ("proposal.docx", "docx", 1024*200),   # 200KB
            ("budget_analysis.xlsx", "xlsx", 1024*150),  # 150KB
            ("requirements.txt", "txt", 1024*10),   # 10KB
            ("logo.png", "png", 1024*300),         # 300KB
        ]
        
        files = []
        num_files = random.randint(2, 4)
        selected_templates = random.sample(file_templates, min(num_files, len(file_templates)))
        
        for i, (name, ext, size) in enumerate(selected_templates):
            file_id = f"hs_file_{deal_id}_{i+1:03d}"
            file_name = f"{deal_id}_{name}"
            file_url = f"https://api.hubapi.com/files/v3/files/{file_id}/download"
            
            files.append(CRMFile(
                file_id=file_id,
                name=file_name,
                size=size + random.randint(-1000, 1000),  # Add some variation
                file_type=ext,
                url=file_url,
                deal_id=deal_id
            ))
        
        return files
    
    def download_file(self, file_url: str) -> bytes:
        """Mock file download"""
        logger.info(f"Downloading file from {file_url}")
        time.sleep(0.2)  # Simulate download time
        return b"Mock file content for HubSpot file"
