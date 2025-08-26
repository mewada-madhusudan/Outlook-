"""
Status bar component for the Outlook Automation Tool
"""

from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar, QHBoxLayout, QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QIcon

class StatusBar(QStatusBar):
    """Custom status bar with additional features"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup status bar UI"""
        self.setFixedHeight(25)
        self.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #e1e5e9;
                color: #605e5c;
            }
            
            QStatusBar::item {
                border: none;
            }
        """)
        
        # Main status message
        self.status_label = QLabel("Ready")
        self.addWidget(self.status_label)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setVisible(False)
        self.addPermanentWidget(self.progress_bar)
        
        # Connection status
        self.connection_status = QLabel("Offline")
        self.connection_status.setStyleSheet("color: #d13438; font-size: 12px;")
        self.addPermanentWidget(self.connection_status)
        
    def show_message(self, message: str, timeout: int = 0):
        """Show a temporary message"""
        self.status_label.setText(message)
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.status_label.setText("Ready"))
    
    def show_progress(self, visible: bool = True):
        """Show or hide progress bar"""
        self.progress_bar.setVisible(visible)
    
    def set_progress(self, value: int):
        """Set progress bar value (0-100)"""
        self.progress_bar.setValue(value)
    
    def set_connection_status(self, connected: bool):
        """Set connection status"""
        if connected:
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("color: #107c10; font-size: 12px;")
        else:
            self.connection_status.setText("Offline")
            self.connection_status.setStyleSheet("color: #d13438; font-size: 12px;")