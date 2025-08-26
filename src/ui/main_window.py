"""
Main window for the Outlook Automation Tool
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                           QSplitter, QStackedWidget, QLabel, QFrame, QPushButton,
                           QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor

from .sidebar import Sidebar
from .pages.dashboard import DashboardPage
from .pages.templates import TemplatesPage
from .pages.quick_actions import QuickActionsPage
from .pages.reminders import RemindersPage
from .pages.attachments import AttachmentsPage
from .pages.rsvp_tracker import RSVPTrackerPage
from .pages.settings import SettingsPage
from .components.status_bar import StatusBar
from .styles.theme_manager import ThemeManager

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        self.current_page = "dashboard"
        
        self.setup_ui()
        self.setup_connections()
        self.setup_window()
        
        # Apply initial theme
        self.theme_manager.apply_theme(self, "light")
        
    def setup_ui(self):
        """Setup the user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter for sidebar and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create sidebar
        self.sidebar = Sidebar()
        splitter.addWidget(self.sidebar)
        
        # Create content area
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create header
        self.header = self.create_header()
        content_layout.addWidget(self.header)
        
        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.pages = {
            "dashboard": DashboardPage(),
            "templates": TemplatesPage(),
            "quick_actions": QuickActionsPage(),
            "reminders": RemindersPage(),
            "attachments": AttachmentsPage(),
            "rsvp_tracker": RSVPTrackerPage(),
            "settings": SettingsPage()
        }
        
        # Add pages to stacked widget
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
        
        splitter.addWidget(content_frame)
        
        # Set splitter proportions
        splitter.setSizes([250, 800])
        splitter.setCollapsible(0, False)
        
        # Create status bar
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)
        
    def create_header(self) -> QWidget:
        """Create the header widget"""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(60)
        header.setFrameStyle(QFrame.Shape.StyledPanel)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Page title
        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("pageTitle")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.page_title.setFont(font)
        layout.addWidget(self.page_title)
        
        layout.addStretch()
        
        # User info and auth status
        self.auth_status = QLabel("Not Connected")
        self.auth_status.setObjectName("authStatus")
        layout.addWidget(self.auth_status)
        
        self.connect_button = QPushButton("Connect to Outlook")
        self.connect_button.setObjectName("connectButton")
        layout.addWidget(self.connect_button)
        
        return header
    
    def setup_connections(self):
        """Setup signal-slot connections"""
        self.sidebar.page_changed.connect(self.change_page)
        self.connect_button.clicked.connect(self.handle_connect)
        
        # Connect dashboard quick actions
        if hasattr(self.pages["dashboard"], "quick_action_triggered"):
            self.pages["dashboard"].quick_action_triggered.connect(self.handle_dashboard_quick_action)
        
        # Connect page-specific signals if needed
        if hasattr(self.pages["settings"], "theme_changed"):
            self.pages["settings"].theme_changed.connect(self.change_theme)
    
    def handle_dashboard_quick_action(self, action: str):
        """Handle quick action from dashboard"""
        if action == "zoom_invite":
            self.change_page("quick_actions")
            # Could also directly open email composer
        elif action == "follow_up":
            self.change_page("quick_actions")
        elif action == "thank_you":
            self.change_page("quick_actions")
        elif action == "attachments":
            self.change_page("attachments")
    
    def setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("Outlook Email Automation Tool")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Center window on screen
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def change_page(self, page_name: str):
        """Change the current page"""
        if page_name in self.pages:
            self.current_page = page_name
            page_widget = self.pages[page_name]
            self.stacked_widget.setCurrentWidget(page_widget)
            
            # Update page title
            page_titles = {
                "dashboard": "Dashboard",
                "templates": "Template Library",
                "quick_actions": "Quick Actions",
                "reminders": "Reminders",
                "attachments": "Attachments",
                "rsvp_tracker": "RSVP Tracker",
                "settings": "Settings"
            }
            
            self.page_title.setText(page_titles.get(page_name, page_name.title()))
            
            # Refresh page if it has a refresh method
            if hasattr(page_widget, "refresh"):
                page_widget.refresh()
    
    def handle_connect(self):
        """Handle Outlook connection"""
        if self.connect_button.text() == "Connect to Outlook":
            self.connect_to_outlook()
        else:
            self.disconnect_from_outlook()
    
    def connect_to_outlook(self):
        """Connect to Microsoft Graph"""
        from core.config import Config
        from core.graph_client import GraphClient
        
        # Get client configuration
        config = Config()
        auth_config = config.auth_config
        
        if not auth_config.client_id:
            from PyQt6.QtWidgets import QMessageBox, QInputDialog
            
            # Prompt for client ID if not configured
            client_id, ok = QInputDialog.getText(
                self, 
                "Microsoft Graph Configuration",
                "Please enter your Azure App Client ID:",
                text=auth_config.client_id
            )
            
            if not ok or not client_id.strip():
                self.status_bar.show_message("Connection cancelled", 3000)
                return
            
            # Save client ID to config
            config.config["auth"]["client_id"] = client_id.strip()
            config.save_config()
            auth_config.client_id = client_id.strip()
        
        self.status_bar.show_message("Connecting to Outlook...", 0)
        self.connect_button.setEnabled(False)
        
        # Create Graph client and authenticate
        self.graph_client = GraphClient(auth_config.client_id, auth_config.tenant_id)
        
        # Run authentication in separate thread to avoid blocking UI
        import threading
        auth_thread = threading.Thread(target=self._authenticate_graph)
        auth_thread.daemon = True
        auth_thread.start()
    
    def _authenticate_graph(self):
        """Authenticate with Microsoft Graph (runs in separate thread)"""
        try:
            success = self.graph_client.authenticate()
            
            # Use QTimer to update UI from main thread
            if success:
                QTimer.singleShot(0, self.on_connection_success)
            else:
                QTimer.singleShot(0, self.on_connection_failed)
                
        except Exception as e:
            print(f"Authentication error: {e}")
            QTimer.singleShot(0, self.on_connection_failed)
    
    def on_connection_success(self):
        """Handle successful connection"""
        try:
            # Get user profile
            user_profile = self.graph_client.get_user_profile()
            user_name = user_profile.get('displayName', 'User') if user_profile else 'User'
            
            self.auth_status.setText(f"Connected as {user_name}")
            self.auth_status.setStyleSheet("color: #107c10; font-weight: bold;")
            self.connect_button.setText("Disconnect")
            self.connect_button.setEnabled(True)
            self.status_bar.show_message("Successfully connected to Outlook!", 5000)
            
            # Update dashboard with connection activity
            if hasattr(self.pages["dashboard"], "add_activity"):
                self.pages["dashboard"].add_activity("🔗 Connected to Microsoft Outlook")
                
        except Exception as e:
            print(f"Error getting user profile: {e}")
            self.auth_status.setText("Connected")
            self.auth_status.setStyleSheet("color: #107c10; font-weight: bold;")
            self.connect_button.setText("Disconnect")
            self.connect_button.setEnabled(True)
            self.status_bar.show_message("Connected to Outlook", 5000)
    
    def on_connection_failed(self):
        """Handle failed connection"""
        self.auth_status.setText("Connection Failed")
        self.auth_status.setStyleSheet("color: #d13438; font-weight: bold;")
        self.connect_button.setText("Connect to Outlook")
        self.connect_button.setEnabled(True)
        self.status_bar.show_message("Failed to connect to Outlook. Please try again.", 5000)
    
    def disconnect_from_outlook(self):
        """Disconnect from Outlook"""
        if hasattr(self, 'graph_client'):
            self.graph_client.disconnect()
            delattr(self, 'graph_client')
        
        self.auth_status.setText("Not Connected")
        self.auth_status.setStyleSheet("color: #605e5c;")
        self.connect_button.setText("Connect to Outlook")
        self.status_bar.show_message("Disconnected from Outlook", 3000)
        
        # Update dashboard with disconnection activity
        if hasattr(self.pages["dashboard"], "add_activity"):
            self.pages["dashboard"].add_activity("🔌 Disconnected from Microsoft Outlook")
    
    def change_theme(self, theme_name: str):
        """Change application theme"""
        self.theme_manager.apply_theme(self, theme_name)
        
        # Update all pages
        for page in self.pages.values():
            if hasattr(page, "update_theme"):
                page.update_theme(theme_name)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window geometry
        # TODO: Save to config
        event.accept()