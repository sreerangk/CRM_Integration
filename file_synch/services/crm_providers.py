from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CRMFile:
    def __init__(self, file_id: str, name: str, size: int, file_type: str, url: str, deal_id: str):
        self.file_id = file_id
        self.name = name
        self.size = size
        self.file_type = file_type
        self.url = url
        self.deal_id = deal_id

class CRMDeal:
    def __init__(self, deal_id: str, name: str, amount: float = None, stage: str = None):
        self.deal_id = deal_id
        self.name = name
        self.amount = amount
        self.stage = stage

class BaseCRMService(ABC):
    """Abstract base class for CRM services for SOLID principles"""
    
    def __init__(self, api_key: str, api_endpoint: str = None):
        self.api_key = api_key
        self.api_endpoint = api_endpoint
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with CRM system"""
        pass
    
    @abstractmethod
    def get_deals(self) -> List[CRMDeal]:
        """Get all deals from CRM"""
        pass
    
    @abstractmethod
    def get_files_for_deal(self, deal_id: str) -> List[CRMFile]:
        """Get all files for a specific deal"""
        pass
    
    @abstractmethod
    def download_file(self, file_url: str) -> bytes:
        """Download file content"""
        pass