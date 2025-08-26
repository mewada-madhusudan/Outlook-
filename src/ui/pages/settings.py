"""
Settings page for the Outlook Automation Tool
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QPushButton, QGroupBox, QFormLayout,
                           QLineEdit, QComboBox, QCheckBox, QSpinBox,
                           QTextEdit, QTabWidget, QFileDialog, QMessageBox,
                           QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class GeneralSettingsTab(QWidget):
    """General settings tab"""
    
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup general settings UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Appearance
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        # Language
        language_combo = QComboBox()
        language_combo.addItems(["English", "Spanish", "French", "German"])
        appearance_layout.addRow("Language:", language_combo)
        
        layout.addWidget(appearance_group)
        
        # Notifications
        notifications_group = QGroupBox("Notifications")
        notifications_layout = QFormLayout(notifications_group)
        
        self.email_notifications_cb = QCheckBox("Email notifications")
        self.email_notifications_cb.setChecked(True)
        notifications_layout.addRow(self.email_notifications_cb)
        
        self.desktop_notifications_cb = QCheckBox("Desktop notifications")
        self.desktop_notifications_cb.setChecked(True)
        notifications_layout.addRow(self.desktop_notifications_cb)
        
        self.sound_notifications_cb = QCheckBox("Sound notifications")
        notifications_layout.addRow(self.sound_notifications_cb)
        
        layout.addWidget(notifications_group)
        
        # Auto-save
        autosave_group = QGroupBox("Auto-save")
        autosave_layout = QFormLayout(autosave_group)
        
        self.autosave_cb = QCheckBox("Enable auto-save")
        self.autosave_cb.setChecked(True)
        autosave_layout.addRow(self.autosave_cb)
        
        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(1, 60)
        self.autosave_interval.setValue(5)
        self.autosave_interval.setSuffix(" minutes")
        autosave_layout.addRow("Save interval:", self.autosave_interval)
        
        layout.addWidget(autosave_group)
        
        layout.addStretch()
    
    def on_theme_changed(self, theme_name: str):
        """Handle theme change"""
        self.theme_changed.emit(theme_name.lower())

class AuthenticationTab(QWidget):
    """Authentication settings tab"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup authentication UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Microsoft Graph
        graph_group = QGroupBox("Microsoft Graph Connection")
        graph_layout = QFormLayout(graph_group)
        
        # Connection status
        self.connection_status = QLabel("Not Connected")
        self.connection_status.setStyleSheet("color: #d13438; font-weight: bold;")
        graph_layout.addRow("Status:", self.connection_status)
        
        # Client ID
        self.client_id_edit = QLineEdit()
        self.client_id_edit.setPlaceholderText("Enter your Azure App Client ID")
        graph_layout.addRow("Client ID:", self.client_id_edit)
        
        # Tenant ID
        self.tenant_id_edit = QLineEdit("common")
        graph_layout.addRow("Tenant ID:", self.tenant_id_edit)
        
        # Connection buttons
        button_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        self.connect_btn.clicked.connect(self.connect_outlook)
        button_layout.addWidget(self.connect_btn)
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a52b2f;
            }
            QPushButton:disabled {
                background-color: #c8c6c4;
            }
        """)
        button_layout.addWidget(self.disconnect_btn)
        
        button_layout.addStretch()
        graph_layout.addRow(button_layout)
        
        layout.addWidget(graph_group)
        
        # Zoom Integration
        zoom_group = QGroupBox("Zoom Integration (Optional)")
        zoom_layout = QFormLayout(zoom_group)
        
        self.zoom_enabled_cb = QCheckBox("Enable Zoom integration")
        zoom_layout.addRow(self.zoom_enabled_cb)
        
        self.zoom_client_id_edit = QLineEdit()
        self.zoom_client_id_edit.setPlaceholderText("Zoom App Client ID")
        zoom_layout.addRow("Zoom Client ID:", self.zoom_client_id_edit)
        
        self.zoom_client_secret_edit = QLineEdit()
        self.zoom_client_secret_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.zoom_client_secret_edit.setPlaceholderText("Zoom App Client Secret")
        zoom_layout.addRow("Zoom Client Secret:", self.zoom_client_secret_edit)
        
        layout.addWidget(zoom_group)
        
        layout.addStretch()
    
    def connect_outlook(self):
        """Connect to Outlook"""
        # TODO: Implement actual Microsoft Graph authentication
        self.connection_status.setText("Connected")
        self.connection_status.setStyleSheet("color: #107c10; font-weight: bold;")
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        QMessageBox.information(self, "Connected", "Successfully connected to Outlook!")

class AdvancedTab(QWidget):
    """Advanced settings tab"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup advanced settings UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Performance
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout(performance_group)
        
        # Batch size
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(10, 100)
        self.batch_size_spin.setValue(25)
        performance_layout.addRow("Batch size:", self.batch_size_spin)
        
        # Sync interval
        self.sync_interval_spin = QSpinBox()
        self.sync_interval_spin.setRange(1, 60)
        self.sync_interval_spin.setValue(5)
        self.sync_interval_spin.setSuffix(" minutes")
        performance_layout.addRow("Sync interval:", self.sync_interval_spin)
        
        # Cache size
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(50, 500)
        self.cache_size_spin.setValue(100)
        self.cache_size_spin.setSuffix(" MB")
        performance_layout.addRow("Cache size:", self.cache_size_spin)
        
        layout.addWidget(performance_group)
        
        # Debug
        debug_group = QGroupBox("Debug & Logging")
        debug_layout = QFormLayout(debug_group)
        
        self.debug_mode_cb = QCheckBox("Enable debug mode")
        debug_layout.addRow(self.debug_mode_cb)
        
        self.verbose_logging_cb = QCheckBox("Verbose logging")
        debug_layout.addRow(self.verbose_logging_cb)
        
        # Log level
        log_level_combo = QComboBox()
        log_level_combo.addItems(["ERROR", "WARNING", "INFO", "DEBUG"])
        log_level_combo.setCurrentText("INFO")
        debug_layout.addRow("Log level:", log_level_combo)
        
        # Log file location
        log_location_layout = QHBoxLayout()
        self.log_location_edit = QLineEdit("./logs/outlook_automation.log")
        log_location_layout.addWidget(self.log_location_edit)
        
        browse_log_btn = QPushButton("Browse")
        browse_log_btn.clicked.connect(self.browse_log_location)
        log_location_layout.addWidget(browse_log_btn)
        
        debug_layout.addRow("Log file:", log_location_layout)
        
        layout.addWidget(debug_group)
        
        # Data Management
        data_group = QGroupBox("Data Management")
        data_layout = QFormLayout(data_group)
        
        # Export data
        export_btn = QPushButton("Export All Data")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #5c2d91;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a1f6b;
            }
        """)
        export_btn.clicked.connect(self.export_data)
        data_layout.addRow("Backup:", export_btn)
        
        # Clear data
        clear_btn = QPushButton("Clear All Data")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #d13438;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #a52b2f;
            }
        """)
        clear_btn.clicked.connect(self.clear_data)
        data_layout.addRow("Reset:", clear_btn)
        
        layout.addWidget(data_group)
        
        layout.addStretch()
    
    def browse_log_location(self):
        """Browse for log file location"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select Log File Location", 
            self.log_location_edit.text(), 
            "Log Files (*.log)"
        )
        if file_path:
            self.log_location_edit.setText(file_path)
    
    def export_data(self):
        """Export application data"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", 
            "outlook_automation_backup.json", 
            "JSON Files (*.json)"
        )
        if file_path:
            # TODO: Implement actual data export
            QMessageBox.information(self, "Export", f"Data exported to {file_path}")
    
    def clear_data(self):
        """Clear all application data"""
        reply = QMessageBox.question(
            self, "Clear Data", 
            "Are you sure you want to clear all data? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # TODO: Implement actual data clearing
            QMessageBox.information(self, "Cleared", "All data has been cleared.")

class SettingsPage(QWidget):
    """Settings page"""
    
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setObjectName("contentPage")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup settings page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        title = QLabel("Settings")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Tab widget
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e1e5e9;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid #e1e5e9;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Add tabs
        self.general_tab = GeneralSettingsTab()
        self.general_tab.theme_changed.connect(self.theme_changed.emit)
        tab_widget.addTab(self.general_tab, "General")
        
        self.auth_tab = AuthenticationTab()
        tab_widget.addTab(self.auth_tab, "Authentication")
        
        self.advanced_tab = AdvancedTab()
        tab_widget.addTab(self.advanced_tab, "Advanced")
        
        layout.addWidget(tab_widget)
        
        # Save buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0e5a0e;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #605e5c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4a4746;
            }
        """)
        button_layout.addWidget(reset_btn)
        
        layout.addLayout(button_layout)
    
    def save_settings(self):
        """Save application settings"""
        # TODO: Implement actual settings saving
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
    
    def refresh(self):
        """Refresh settings page"""
        pass