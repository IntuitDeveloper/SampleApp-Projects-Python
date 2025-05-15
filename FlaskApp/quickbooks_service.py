import requests
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class QuickBooksService:
    """Service for handling QuickBooks API interactions"""
    
    BASE_URL = 'https://quickbooks.api.intuit.com'
    
    def __init__(self, auth_header: str, realm_id: str):
        self.auth_header = auth_header
        self.realm_id = realm_id
        
    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for QuickBooks API requests"""
        return {
            'Authorization': self.auth_header,
            'Accept': 'application/json',
            'Content-Type': 'application/text'
        }
        
    def _make_request(self, endpoint: str, method: str = "POST", data: Optional[str] = None) -> Dict:
        """
        Make a request to QuickBooks API
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            
        Returns:
            Dict containing API response
        """
        url = f'{self.BASE_URL}{endpoint}'
        try:
            response = requests.request(
                method,
                url,
                headers=self._get_headers(),
                data=data
            )
            response.raise_for_status()
            return json.loads(response.text)
        except requests.exceptions.RequestException as e:
            logger.error(f"QuickBooks API request failed: {str(e)}")
            raise
            
    def get_customers(self) -> Dict[str, str]:
        """
        Fetch customers from QuickBooks
        
        Returns:
            Dict mapping customer IDs to their fully qualified names
        """
        try:
            endpoint = f'/v3/company/{self.realm_id}/query'
            query = "Select * from Customer where Job = false"
            
            data = self._make_request(endpoint, data=query)
            customers = data['QueryResponse']['Customer']
            
            return {
                customer['Id']: customer['FullyQualifiedName']
                for customer in customers
                if 'Id' in customer
            }
        except Exception as e:
            logger.error(f"Error fetching customers: {str(e)}")
            raise
            
    def get_customer_names(self) -> List[str]:
        """
        Get list of customer names
        
        Returns:
            List of customer names
        """
        customers = self.get_customers()
        return list(customers.values()) 