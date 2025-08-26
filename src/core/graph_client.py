"""
Microsoft Graph API client for Outlook integration
"""

import asyncio
import json
import webbrowser
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import requests
from urllib.parse import urlencode, parse_qs, urlparse
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

logger = logging.getLogger(__name__)

class AuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback"""
    
    def do_GET(self):
        # Parse query parameters
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' in query_params:
            # Store the authorization code
            self.server.auth_code = query_params['code'][0]
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            success_html = """
            <html>
            <head><title>Authorization Successful</title></head>
            <body>
                <h2>Authorization successful!</h2>
                <p>You can now close this window and return to the application.</p>
                <script>setTimeout(() => window.close(), 3000);</script>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            # Send error response
            self.send_response(400)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            error_html = """
            <html>
            <head><title>Authorization Failed</title></head>
            <body>
                <h2>Authorization failed!</h2>
                <p>Please try again.</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

class GraphClient:
    """Microsoft Graph API client"""
    
    def __init__(self, client_id: str, tenant_id: str = "common"):
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.redirect_uri = "http://localhost:8080/callback"
        self.scopes = [
            "Mail.ReadWrite",
            "Mail.Send", 
            "MailboxSettings.Read",
            "Calendars.ReadWrite",
            "User.Read",
            "offline_access"
        ]
        
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # API endpoints
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
    
    def get_auth_url(self) -> str:
        """Get authorization URL for OAuth flow"""
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'response_mode': 'query'
        }
        
        auth_url = f"{self.authority}/oauth2/v2.0/authorize?" + urlencode(params)
        return auth_url
    
    def authenticate(self) -> bool:
        """Perform OAuth authentication flow"""
        try:
            # Start local HTTP server for callback
            server = HTTPServer(('localhost', 8080), AuthCallbackHandler)
            server.auth_code = None
            server.timeout = 60  # 60 second timeout
            
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
                # Exchange code for tokens
                return self._exchange_code_for_tokens(server.auth_code)
            else:
                logger.error("Authentication timeout or failed")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def _exchange_code_for_tokens(self, auth_code: str) -> bool:
        """Exchange authorization code for access tokens"""
        try:
            token_url = f"{self.authority}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.client_id,
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': self.redirect_uri,
                'scope': ' '.join(self.scopes)
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now(timezone.utc).timestamp() + expires_in
            
            return True
            
        except Exception as e:
            logger.error(f"Token exchange error: {e}")
            return False
    
    def refresh_access_token(self) -> bool:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            return False
        
        try:
            token_url = f"{self.authority}/oauth2/v2.0/token"
            
            data = {
                'client_id': self.client_id,
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'scope': ' '.join(self.scopes)
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now(timezone.utc).timestamp() + expires_in
            
            return True
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False
    
    def _ensure_valid_token(self) -> bool:
        """Ensure we have a valid access token"""
        if not self.access_token:
            return False
        
        # Check if token is expired (with 5 minute buffer)
        if self.token_expires_at and (datetime.now(timezone.utc).timestamp() + 300) > self.token_expires_at:
            return self.refresh_access_token()
        
        return True
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated request to Graph API"""
        if not self._ensure_valid_token():
            raise Exception("No valid access token")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.graph_endpoint}{endpoint}"
        
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
            logger.error(f"Graph API request error: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            raise
    
    def get_user_profile(self) -> Optional[Dict]:
        """Get current user profile"""
        return self._make_request('GET', '/me')
    
    def get_messages(self, folder: str = 'inbox', limit: int = 10) -> List[Dict]:
        """Get messages from specified folder"""
        params = {
            '$top': limit,
            '$orderby': 'receivedDateTime desc',
            '$select': 'id,subject,from,toRecipients,receivedDateTime,bodyPreview,isRead'
        }
        
        response = self._make_request('GET', f'/me/mailFolders/{folder}/messages', params=params)
        return response.get('value', []) if response else []
    
    def create_draft(self, message_data: Dict) -> Optional[Dict]:
        """Create email draft"""
        return self._make_request('POST', '/me/messages', data=message_data)
    
    def send_email(self, message_data: Dict) -> bool:
        """Send email directly"""
        try:
            self._make_request('POST', '/me/sendMail', data={'message': message_data})
            return True
        except Exception as e:
            logger.error(f"Send email error: {e}")
            return False
    
    def get_folders(self) -> List[Dict]:
        """Get mail folders"""
        response = self._make_request('GET', '/me/mailFolders')
        return response.get('value', []) if response else []
    
    def get_signature(self) -> Optional[str]:
        """Get user's email signature"""
        try:
            response = self._make_request('GET', '/me/mailboxSettings')
            if response and 'automaticRepliesSetting' in response:
                return response.get('automaticRepliesSetting', {}).get('internalReplyMessage', '')
            return None
        except Exception:
            return None
    
    def create_calendar_event(self, event_data: Dict) -> Optional[Dict]:
        """Create calendar event"""
        return self._make_request('POST', '/me/events', data=event_data)
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self.access_token is not None and self._ensure_valid_token()
    
    def disconnect(self):
        """Clear authentication tokens"""
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None