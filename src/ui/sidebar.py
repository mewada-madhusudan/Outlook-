"""
Sidebar navigation for the Outlook Automation Tool
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QFrame, QScrollArea, QSizePolicy, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QPalette

class SidebarButton(QPushButton):
    """Custom sidebar navigation button"""
    
    def __init__(self, text: str, icon_name: str = None, page_name: str = None):
        super().__init__(text)
        self.page_name = page_name or text.lower().replace(" ", "_")
        
        self.setObjectName("sidebarButton")
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(45)
        
        # Set text alignment
        self.setStyleSheet("""
            QPushButton#sidebarButton {
                text-align: left;
                padding: 10px 15px;
                border: none;
                background-color: transparent;
                color: #333;
                font-size: 14px;
                border-radius: 6px;
                margin: 2px 8px;
            }
            QPushButton#sidebarButton:hover {
                background-color: rgba(0, 120, 212, 0.1);
            }
            QPushButton#sidebarButton:checked {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
            }
        """)

class Sidebar(QWidget):
    """Sidebar navigation widget"""
    
    page_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.button_group = QButtonGroup()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the sidebar UI"""
        self.setObjectName("sidebar")
        self.setFixedWidth(250)
        self.setStyleSheet("""
            QWidget#sidebar {
                background-color: #f8f9fa;
                border-right: 1px solid #e1e5e9;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create header
        header = self.create_header()
        layout.addWidget(header)
        
        # Create scroll area for navigation
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create navigation widget
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 10, 0, 10)
        nav_layout.setSpacing(5)
        
        # Navigation sections
        sections = [
            {
                "title": "Main",
                "items": [
                    ("Dashboard", "dashboard", "dashboard"),
                    ("Template Library", "templates", "templates"),
                    ("Quick Actions", "quick_actions", "quick_actions")
                ]
            },
            {
                "title": "Tracking",
                "items": [
                    ("Reminders", "reminders", "reminders"),
                    ("RSVP Tracker", "rsvp_tracker", "rsvp_tracker"),
                    ("Attachments", "attachments", "attachments")
                ]
            },
            {
                "title": "System",
                "items": [
                    ("Settings", "settings", "settings")
                ]
            }
        ]
        
        for section in sections:
            # Add section header
            section_label = QLabel(section["title"])
            section_label.setObjectName("sectionLabel")
            section_label.setStyleSheet("""
                QLabel#sectionLabel {
                    color: #666;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 15px 15px 5px 15px;
                    text-transform: uppercase;
                }
            """)
            nav_layout.addWidget(section_label)
            
            # Add section items
            for item_text, icon_name, page_name in section["items"]:
                button = SidebarButton(item_text, icon_name, page_name)
                self.button_group.addButton(button)
                button.clicked.connect(lambda checked, pn=page_name: self.page_changed.emit(pn))
                nav_layout.addWidget(button)
            
            # Add spacing between sections
            nav_layout.addSpacing(10)
        
        nav_layout.addStretch()
        
        scroll_area.setWidget(nav_widget)
        layout.addWidget(scroll_area)
        
        # Set default selection
        if self.button_group.buttons():
            self.button_group.buttons()[0].setChecked(True)
    
    def create_header(self) -> QWidget:
        """Create the sidebar header"""
        header = QFrame()
        header.setObjectName("sidebarHeader")
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame#sidebarHeader {
                background-color: #0078d4;
                border-bottom: 1px solid #106ebe;
            }
        """)
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # App title
        title = QLabel("Email Automation")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title)
        
        # Version
        version = QLabel("v1.0.0")
        version.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
            }
        """)
        layout.addWidget(version)
        
        return header