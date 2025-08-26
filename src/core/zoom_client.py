"""
Zoom API client for meeting integration
"""

import requests
import base64
import json
import webbrowser
import threading
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

logger = logging.getLogger(__name__)

class ZoomCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for Zoom OAuth callback"""
    
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' in query_params:
            self.server.auth_code = query_params['code'][0]
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            success_html = """
            <html>
            <head><title>Zoom Authorization Successful</title></head>
            <body>
                <h2>Zoom authorization successful!</h2>
                <p>You can now close this window and return to the application.</p>
                <script>setTimeout(() => window.close(), 3000);</script>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            self.send_response(400)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            error_html = """
            <html>
            <head><title>Zoom Authorization Failed</title></head>
            <body>
                <h2>Zoom authorization failed!</h2>
                <p>Please try again.</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        pass

class ZoomClient:
    """Zoom API client for meeting management"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = "http://localhost:8081/zoom/callback"
        self.scopes = ["meeting:write", "meeting:read", "user:read"]
        
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # API endpoints
        self.auth_endpoint = "https://zoom.us/oauth"
        self.api_endpoint = "https://api.zoom.us/v2"
    
    def get_auth_url(self) -> str:
        """Get authorization URL for OAuth flow"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes)
        }
        
        auth_url = f"{self.auth_endpoint}/authorize?" + urlencode(params)
        return auth_url
    
    def authenticate(self) -> bool:
        """Perform OAuth authentication flow"""
        try:
            # Start local HTTP server for callback
            server = HTTPServer(('localhost', 8081), ZoomCallbackHandler)
            server.auth_code = None
            server.timeout = 60
            
            # Start server in background thread
            server_thread = threading.Thread(target=server.handle_request)
            server_thread.daemon = True
            server_thread.start()
            
            # Open browser for authentication
            auth_url = self.get_auth_url()
            webbrowser.open(auth_url)
            
            # Wait for callback
            start_time = time.time()
            while server.auth_code is None and (time.time() - start_time) < 60:
                time.sleep(0.5)
            
            if server.auth_code:
                return self._exchange_code_for_tokens(server.auth_code)
            else:
                logger.error("Zoom authentication timeout or failed")
                return False
                
        except Exception as e:
            logger.error(f"Zoom authentication error: {e}")
            return False
    
    def _exchange_code_for_tokens(self, auth_code: str) -> bool:
        """Exchange authorization code for access tokens"""
        try:
            token_url = f"{self.auth_endpoint}/token"
            
            # Create basic auth header
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now(timezone.utc).timestamp() + expires_in
            
            return True
            
        except Exception as e:
            logger.error(f"Zoom token exchange error: {e}")
            return False
    
    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            return False
        
        try:
            token_url = f"{self.auth_endpoint}/token"
            
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            
            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now(timezone.utc).timestamp() + expires_in
            
            return True
            
        except Exception as e:
            logger.error(f"Zoom token refresh error: {e}")
            return False
    
    def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token"""
        if not self.access_token:
            return False
        
        if self.token_expires_at and (datetime.now(timezone.utc).timestamp() + 300) > self.token_expires_at:
            return self.refresh_access_token()
        
        return True
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated request to Zoom API"""
        if not self._ensure_valid_token():
            raise Exception("No valid Zoom access token")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.api_endpoint}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Zoom API request error: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    def get_user_info(self) -> Optional[Dict]:
        """Get current user information"""
        return self._make_request('GET', '/users/me')
    
    def create_meeting(self, meeting_data: Dict) -> Optional[Dict]:
        """Create a Zoom meeting"""
        default_settings = {
            'host_video': True,
            'participant_video': True,
            'join_before_host': False,
            'mute_upon_entry': True,
            'watermark': False,
            'use_pmi': False,
            'approval_type': 0,
            'audio': 'both',
            'auto_recording': 'none'
        }
        
        # Merge with provided data
        if 'settings' in meeting_data:
            meeting_data['settings'].update(default_settings)
        else:
            meeting_data['settings'] = default_settings
        
        return self._make_request('POST', '/users/me/meetings', data=meeting_data)
    
    def get_meetings(self, meeting_type: str = 'scheduled') -> List[Dict]:
        """Get user's meetings"""
        params = {'type': meeting_type}
        response = self._make_request('GET', '/users/me/meetings', params=params)
        return response.get('meetings', []) if response else []
    
    def get_meeting(self, meeting_id: str) -> Optional[Dict]:
        """Get specific meeting details"""
        return self._make_request('GET', f'/meetings/{meeting_id}')
    
    def update_meeting(self, meeting_id: str, meeting_data: Dict) -> Optional[Dict]:
        """Update a meeting"""
        return self._make_request('PATCH', f'/meetings/{meeting_id}', data=meeting_data)
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting"""
        try:
            self._make_request('DELETE', f'/meetings/{meeting_id}')
            return True
        except Exception as e:
            logger.error(f"Delete meeting error: {e}")
            return False
    
    def create_quick_meeting(self, topic: str, duration: int = 60, start_time: Optional[datetime] = None) -> Optional[Dict]:
        """Create a quick meeting with minimal configuration"""
        if start_time is None:
            start_time = datetime.now(timezone.utc) + timedelta(minutes=5)
        
        meeting_data = {
            'topic': topic,
            'type': 2,  # Scheduled meeting
            'start_time': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'duration': duration,
            'timezone': 'UTC',
            'settings': {
                'host_video': True,
                'participant_video': True,
                'join_before_host': True,
                'mute_upon_entry': True,
                'waiting_room': False
            }
        }
        
        return self.create_meeting(meeting_data)
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.access_token is not None and self._ensure_valid_token()
    
    def disconnect(self):
        """Clear authentication tokens"""
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None