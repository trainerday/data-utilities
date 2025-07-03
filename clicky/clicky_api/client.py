import requests
from typing import Dict, List, Optional, Union
from datetime import datetime, date
import json
from urllib.parse import urlencode


class ClickyAPIClient:
    """Client for interacting with the Clicky Analytics API."""
    
    BASE_URL = "https://api.clicky.com/api/stats/4"
    
    def __init__(self, site_id: str, sitekey: str):
        """
        Initialize the Clicky API client.
        
        Args:
            site_id: Your Clicky site ID
            sitekey: Your Clicky sitekey for authentication
        """
        self.site_id = site_id
        self.sitekey = sitekey
        self.session = requests.Session()
    
    def _make_request(self, params: Dict[str, Union[str, int]]) -> Union[Dict, List]:
        """
        Make a request to the Clicky API.
        
        Args:
            params: Dictionary of parameters to send
            
        Returns:
            Parsed JSON response
            
        Raises:
            requests.exceptions.RequestException: For HTTP errors
            ValueError: For JSON parsing errors
        """
        # Add authentication
        params['site_id'] = self.site_id
        params['sitekey'] = self.sitekey
        
        # Default to JSON output if not specified
        if 'output' not in params:
            params['output'] = 'json'
        
        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        if params.get('output') == 'json':
            return response.json()
        else:
            return response.text
    
    def get_stats(
        self,
        stat_type: Union[str, List[str]],
        date_range: str = "today",
        limit: Optional[int] = None,
        output: str = "json",
        **kwargs
    ) -> Union[Dict, List, str]:
        """
        Get statistics from Clicky.
        
        Args:
            stat_type: Type(s) of statistics to retrieve (e.g., 'visitors', 'actions', 'pages')
            date_range: Date range for the stats (e.g., 'today', 'yesterday', 'last-7-days')
            limit: Maximum number of results to return
            output: Output format ('json', 'xml', 'csv', 'php')
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Statistics data in the requested format
        """
        params = {
            'type': stat_type if isinstance(stat_type, str) else ','.join(stat_type),
            'date': date_range,
            'output': output
        }
        
        if limit:
            params['limit'] = limit
        
        # Add any additional parameters
        params.update(kwargs)
        
        return self._make_request(params)
    
    def get_visitors(self, date_range: str = "today", **kwargs) -> Union[Dict, List]:
        """Get visitor statistics."""
        return self.get_stats('visitors', date_range, **kwargs)
    
    def get_actions(self, date_range: str = "today", **kwargs) -> Union[Dict, List]:
        """Get action statistics."""
        return self.get_stats('actions', date_range, **kwargs)
    
    def get_pages(self, date_range: str = "today", limit: int = 20, **kwargs) -> Union[Dict, List]:
        """Get page statistics."""
        return self.get_stats('pages', date_range, limit=limit, **kwargs)
    
    def get_referrers(self, date_range: str = "today", limit: int = 20, **kwargs) -> Union[Dict, List]:
        """Get referrer statistics."""
        return self.get_stats('referring-domains', date_range, limit=limit, **kwargs)
    
    def get_searches(self, date_range: str = "today", limit: int = 20, **kwargs) -> Union[Dict, List]:
        """Get search keyword statistics."""
        return self.get_stats('searches', date_range, limit=limit, **kwargs)
    
    def get_countries(self, date_range: str = "today", limit: int = 20, **kwargs) -> Union[Dict, List]:
        """Get country statistics."""
        return self.get_stats('countries', date_range, limit=limit, **kwargs)
    
    def get_browsers(self, date_range: str = "today", limit: int = 20, **kwargs) -> Union[Dict, List]:
        """Get browser statistics."""
        return self.get_stats('browsers', date_range, limit=limit, **kwargs)
    
    def get_operating_systems(self, date_range: str = "today", limit: int = 20, **kwargs) -> Union[Dict, List]:
        """Get operating system statistics."""
        return self.get_stats('operating-systems', date_range, limit=limit, **kwargs)
    
    def get_multiple_stats(
        self,
        stat_types: List[str],
        date_range: str = "today",
        **kwargs
    ) -> Union[Dict, List]:
        """
        Get multiple types of statistics in a single request.
        
        Args:
            stat_types: List of statistic types to retrieve
            date_range: Date range for the stats
            **kwargs: Additional parameters
            
        Returns:
            Combined statistics data
        """
        return self.get_stats(stat_types, date_range, **kwargs)
    
    def get_custom_date_range(
        self,
        stat_type: Union[str, List[str]],
        start_date: Union[str, date],
        end_date: Union[str, date],
        **kwargs
    ) -> Union[Dict, List]:
        """
        Get statistics for a custom date range.
        
        Args:
            stat_type: Type(s) of statistics to retrieve
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            **kwargs: Additional parameters
            
        Returns:
            Statistics data for the custom date range
        """
        # Convert date objects to strings if necessary
        if isinstance(start_date, date):
            start_date = start_date.strftime('%Y-%m-%d')
        if isinstance(end_date, date):
            end_date = end_date.strftime('%Y-%m-%d')
        
        date_range = f"{start_date},{end_date}"
        return self.get_stats(stat_type, date_range, **kwargs)